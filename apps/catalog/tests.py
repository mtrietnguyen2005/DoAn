"""Kiểm thử danh mục sản phẩm và đánh giá."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import Brand, Category, Product, Review
from apps.inventory.models import Batch

User = get_user_model()


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="VGA")
        self.brand = Brand.objects.create(name="ASUS")
        self.product = Product.objects.create(
            name="RTX 4060 OC", sku="VGA001", category=self.category, brand=self.brand,
            price=Decimal(8000000), sale_price=Decimal(7000000),
            specifications="GPU: RTX 4060\nBộ nhớ: 8GB GDDR6",
        )

    def test_slug_is_generated_and_unique(self):
        other = Product.objects.create(
            name="RTX 4060 OC", sku="VGA002", category=self.category, brand=self.brand, price=Decimal(8000000)
        )
        self.assertEqual(self.product.slug, "rtx-4060-oc")
        self.assertEqual(other.slug, "rtx-4060-oc-2")

    def test_final_price_uses_sale_price(self):
        self.assertEqual(self.product.final_price, Decimal(7000000))
        self.assertTrue(self.product.has_discount)
        self.assertEqual(self.product.discount_percent, 12)  # 12,5% làm tròn xuống

    def test_final_price_ignores_higher_sale_price(self):
        self.product.sale_price = Decimal(9000000)
        self.assertEqual(self.product.final_price, Decimal(8000000))
        self.assertFalse(self.product.has_discount)

    def test_spec_lines_parsing(self):
        self.assertEqual(self.product.spec_lines, [("GPU", "RTX 4060"), ("Bộ nhớ", "8GB GDDR6")])

    def test_stock_reflects_batches(self):
        self.assertEqual(self.product.stock_quantity, 0)
        self.assertFalse(self.product.in_stock)
        Batch.objects.create(product=self.product, batch_code="V1", quantity_in=5,
                             quantity_remaining=5, cost_price=Decimal(6000000))
        self.assertEqual(self.product.stock_quantity, 5)
        self.assertTrue(self.product.in_stock)


class ReviewViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="nguoidung", email="nd@test.vn", password="matkhau123")
        self.category = Category.objects.create(name="RAM")
        self.brand = Brand.objects.create(name="Corsair")
        self.product = Product.objects.create(
            name="Vengeance 16GB", sku="RAM009", category=self.category, brand=self.brand, price=Decimal(1500000)
        )

    def test_login_required_to_create_review(self):
        response = self.client.post(
            reverse("catalog:review_create", args=[self.product.slug]),
            {"rating": 5, "content": "Tốt"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_update_delete_review(self):
        self.client.force_login(self.user)
        self.client.post(reverse("catalog:review_create", args=[self.product.slug]),
                         {"rating": 4, "title": "Ổn", "content": "Chạy tốt"})
        review = Review.objects.get()
        self.assertEqual(review.rating, 4)

        self.client.post(reverse("catalog:review_update", args=[review.pk]),
                         {"rating": 5, "title": "Rất ổn", "content": "Đã dùng 1 tháng"})
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)

        self.client.post(reverse("catalog:review_delete", args=[review.pk]))
        self.assertEqual(Review.objects.count(), 0)

    def test_one_review_per_user_per_product(self):
        self.client.force_login(self.user)
        for _ in range(2):
            self.client.post(reverse("catalog:review_create", args=[self.product.slug]),
                             {"rating": 5, "content": "Tốt"})
        self.assertEqual(Review.objects.filter(product=self.product, user=self.user).count(), 1)

    def test_user_cannot_edit_other_users_review(self):
        other = User.objects.create_user(username="khac", email="k@test.vn", password="matkhau123")
        review = Review.objects.create(product=self.product, user=other, rating=3, content="Bình thường")
        self.client.force_login(self.user)
        response = self.client.post(reverse("catalog:review_update", args=[review.pk]),
                                    {"rating": 1, "content": "Phá hoại"})
        self.assertEqual(response.status_code, 404)
        review.refresh_from_db()
        self.assertEqual(review.rating, 3)


class ProductListFilterTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="SSD")
        self.other_category = Category.objects.create(name="HDD")
        self.brand = Brand.objects.create(name="Samsung")
        self.other_brand = Brand.objects.create(name="WD")
        self.cheap = Product.objects.create(name="SSD 256GB", sku="S1", category=self.category,
                                            brand=self.brand, price=Decimal(800000))
        self.expensive = Product.objects.create(name="SSD 2TB", sku="S2", category=self.category,
                                                brand=self.other_brand, price=Decimal(5000000))
        Batch.objects.create(product=self.cheap, batch_code="S1B", quantity_in=3,
                             quantity_remaining=3, cost_price=Decimal(600000))

    def _names(self, response):
        return {p.name for p in response.context["products"]}

    def test_filter_by_keyword(self):
        response = self.client.get(reverse("catalog:product_list"), {"q": "2TB"})
        self.assertEqual(self._names(response), {"SSD 2TB"})

    def test_filter_by_brand(self):
        response = self.client.get(reverse("catalog:product_list"), {"brand": self.brand.slug})
        self.assertEqual(self._names(response), {"SSD 256GB"})

    def test_filter_by_price_range(self):
        response = self.client.get(reverse("catalog:product_list"), {"min_price": 1000000})
        self.assertEqual(self._names(response), {"SSD 2TB"})

    def test_filter_in_stock_only(self):
        response = self.client.get(reverse("catalog:product_list"), {"in_stock": "1"})
        self.assertEqual(self._names(response), {"SSD 256GB"})

    def test_htmx_request_returns_partial(self):
        response = self.client.get(reverse("catalog:product_list"), HTTP_HX_REQUEST="true")
        self.assertTemplateUsed(response, "catalog/partials/product_grid.html")
        self.assertTemplateNotUsed(response, "base.html")
