"""Kiểm thử giỏ hàng, dashboard admin và phân quyền chỉ đọc trong Admin."""
import re
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product, Review
from apps.inventory.models import Batch
from apps.orders.models import Order

User = get_user_model()


class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="CPU")
        self.brand = Brand.objects.create(name="AMD")
        self.product = Product.objects.create(
            name="Ryzen 5", sku="CPU100", category=self.category, brand=self.brand,
            price=Decimal(5000000), sale_price=Decimal(4500000),
        )
        Batch.objects.create(product=self.product, batch_code="C1", quantity_in=5,
                             quantity_remaining=5, cost_price=Decimal(3800000))

    def test_add_to_cart(self):
        response = self.client.post(reverse("orders:cart_add", args=[self.product.pk]),
                                    {"quantity": 2}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.json()["count"], 2)

    def test_cart_uses_sale_price(self):
        self.client.post(reverse("orders:cart_add", args=[self.product.pk]), {"quantity": 2})
        response = self.client.get(reverse("orders:cart_detail"))
        self.assertEqual(response.context["subtotal"], Decimal(9000000))

    def test_cart_quantity_capped_by_stock(self):
        response = self.client.post(reverse("orders:cart_add", args=[self.product.pk]),
                                    {"quantity": 99}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.json()["count"], 5)

    def test_update_and_remove_cart_item(self):
        self.client.post(reverse("orders:cart_add", args=[self.product.pk]), {"quantity": 3})
        self.client.post(reverse("orders:cart_update", args=[self.product.pk]),
                         {"quantity": 1}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        response = self.client.get(reverse("orders:cart_count"))
        self.assertEqual(response.json()["count"], 1)

        self.client.post(reverse("orders:cart_remove", args=[self.product.pk]),
                         HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(self.client.get(reverse("orders:cart_count")).json()["count"], 0)

    def test_cart_sync_from_localstorage(self):
        response = self.client.post(
            reverse("orders:cart_sync"),
            data='{"items": {"%s": 2}}' % self.product.pk,
            content_type="application/json",
        )
        self.assertEqual(response.json()["count"], 2)

    def test_cart_survives_login_session(self):
        user = User.objects.create_user(username="khach", email="k@test.vn", password="matkhau123")
        self.client.post(reverse("orders:cart_add", args=[self.product.pk]), {"quantity": 2})
        self.client.login(username="khach", password="matkhau123")
        self.assertEqual(self.client.get(reverse("orders:cart_count")).json()["count"], 2)

    def test_checkout_requires_login(self):
        self.client.post(reverse("orders:cart_add", args=[self.product.pk]), {"quantity": 1})
        response = self.client.get(reverse("orders:checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class AdminReadOnlyPermissionTests(TestCase):
    """Địa chỉ, Đánh giá và Giao dịch kho phải ở chế độ chỉ đọc với Admin thường."""

    READ_ONLY_URLS = [
        "/admin/accounts/address/",
        "/admin/catalog/review/",
        "/admin/inventory/stocktransaction/",
    ]

    def setUp(self):
        self.staff = User.objects.create_user(
            username="nhanvien", email="nv@test.vn", password="matkhau123", is_staff=True
        )
        self.staff.user_permissions.set(Permission.objects.all())
        self.superuser = User.objects.create_superuser(
            username="sepwr", email="sep@test.vn", password="matkhau123"
        )

    def test_staff_can_view_but_not_add(self):
        self.client.force_login(self.staff)
        for url in self.READ_ONLY_URLS:
            self.assertEqual(self.client.get(url).status_code, 200, url)
            self.assertEqual(self.client.get(url + "add/").status_code, 403, url)

    def test_staff_can_still_edit_products(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get("/admin/catalog/product/add/").status_code, 200)

    def test_superuser_has_full_access(self):
        self.client.force_login(self.superuser)
        for url in self.READ_ONLY_URLS:
            self.assertEqual(self.client.get(url + "add/").status_code, 200, url)

    def test_staff_cannot_change_review(self):
        category = Category.objects.create(name="RAM")
        brand = Brand.objects.create(name="Kingston")
        product = Product.objects.create(name="Fury 16GB", sku="R1", category=category,
                                         brand=brand, price=Decimal(1500000))
        review = Review.objects.create(product=product, user=self.staff, rating=5, content="Tốt")
        self.client.force_login(self.staff)
        response = self.client.post(f"/admin/catalog/review/{review.pk}/change/",
                                    {"rating": 1, "content": "Sửa trộm"})
        self.assertEqual(response.status_code, 403)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)


class DashboardQueryTests(TestCase):
    """Bảo vệ trang Dashboard khỏi lỗi ORDER BY / GROUP BY của SQL Server.

    SQL Server từ chối câu lệnh có ``ORDER BY`` trên cột không nằm trong ``GROUP BY``
    (lỗi 8127), trong khi SQLite thì bỏ qua. Driver ``mssql-django`` lại giữ nguyên
    ``ORDER BY`` mặc định của model khi câu lệnh có ``GROUP BY``, nên mọi truy vấn
    gom nhóm đều phải gọi ``.order_by()`` để xoá ordering mặc định.
    """

    COLUMN_RE = re.compile(r'"(\w+)"\."(\w+)"')

    def setUp(self):
        self.request = RequestFactory().get("/admin/")
        self.request.user = User.objects.create_superuser(
            username="sep", email="sep@test.vn", password="matkhau123"
        )
        category = Category.objects.create(name="CPU")
        brand = Brand.objects.create(name="Intel")
        product = Product.objects.create(
            name="Core i5", sku="CPU001", category=category, brand=brand, price=Decimal(5000000)
        )
        Batch.objects.create(
            product=product, batch_code="B1", quantity_in=3, quantity_remaining=3,
            cost_price=Decimal(4000000), expiry_date=timezone.localdate() + timedelta(days=5),
        )

    def _capture(self):
        from apps.core.dashboard import dashboard_callback

        with CaptureQueriesContext(connection) as ctx:
            context = dashboard_callback(self.request, {})
            # Ép lượng giá các queryset lười để chúng thực sự chạy
            for key in ("expiring_batches", "low_stock_products", "recent_orders"):
                list(context[key])
        return context, ctx.captured_queries

    def test_dashboard_runs_and_returns_expected_keys(self):
        context, _ = self._capture()
        for key in ("stat_cards", "revenue_month", "profit_month", "order_status_counts",
                    "expiring_batches", "low_stock_products", "recent_orders"):
            self.assertIn(key, context)
        self.assertEqual(len(context["stat_cards"]), 4)

    def test_no_order_by_column_outside_group_by(self):
        """Mọi cột trong ORDER BY phải có mặt trong GROUP BY của cùng câu lệnh."""
        _, queries = self._capture()
        checked = 0
        for entry in queries:
            sql = entry["sql"]
            upper = sql.upper()
            start = upper.find("GROUP BY")
            if start == -1:
                continue
            order_at = upper.rfind("ORDER BY")
            if order_at <= start:
                continue
            checked += 1
            group_clause = sql[start:order_at]
            order_clause = sql[order_at:]
            for table, column in self.COLUMN_RE.findall(order_clause):
                self.assertIn(
                    f'"{table}"."{column}"', group_clause,
                    msg=(f'Cột "{table}"."{column}" nằm trong ORDER BY nhưng không có trong '
                         f"GROUP BY — SQL Server sẽ báo lỗi 8127.\nSQL: {sql[:400]}"),
                )
        self.assertGreaterEqual(len(queries), 1)

    def test_grouped_order_queryset_carries_no_default_ordering(self):
        """Truy vấn gom nhóm trên Order phải sạch ordering dù model có Meta.ordering."""
        from django.db.models import Count

        self.assertEqual(Order._meta.ordering, ["-created_at"])
        grouped = Order.objects.order_by().values("status").annotate(c=Count("id"))
        self.assertEqual(grouped.query.order_by, ())
        self.assertNotIn("ORDER BY", str(grouped.query).upper())
