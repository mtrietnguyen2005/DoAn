import re
from datetime import timedelta
from decimal import Decimal

import pytest
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from apps.core.dashboard import dashboard_callback

pytestmark = pytest.mark.django_db

COLUMN_RE = re.compile(r'"(\w+)"\."(\w+)"')
LAZY_KEYS = ("low_stock_products", "recent_orders")


@pytest.fixture
def dashboard_request(superuser):
    request = RequestFactory().get("/admin/")
    request.user = superuser
    return request


@pytest.fixture
def du_lieu_dashboard(product_with_batches, order, batch_factory, product_factory):
    sap_het = product_factory(name="Hàng sắp hết", sku="LOW001")
    batch_factory(sap_het, quantity=2, cost_price=100000,
                  received_days_ago=3, batch_code="LO-SAPHETTON")
    return {"order": order}


def chay_dashboard(request):
    with CaptureQueriesContext(connection) as ctx:
        context = dashboard_callback(request, {})
        for key in LAZY_KEYS:
            list(context[key])
    return context, ctx.captured_queries


class TestDashboard:
    def test_tra_ve_du_cac_muc_thong_ke(self, dashboard_request, du_lieu_dashboard):
        context, _ = chay_dashboard(dashboard_request)
        for key in ("stat_cards", "revenue_month", "profit_month", "order_status_counts",
                    "low_stock_products", "recent_orders"):
            assert key in context
        assert len(context["stat_cards"]) == 4

    def test_dem_don_hang_theo_trang_thai(self, dashboard_request, du_lieu_dashboard):
        context, _ = chay_dashboard(dashboard_request)
        theo_trang_thai = {r["code"]: r["value"] for r in context["order_status_counts"]}
        assert theo_trang_thai["pending"] == 1

    def test_liet_ke_san_pham_sap_het_ton_kho(self, dashboard_request, du_lieu_dashboard):
        context, _ = chay_dashboard(dashboard_request)
        assert "LOW001" in [p.sku for p in context["low_stock_products"]]

    def test_moi_cot_trong_order_by_deu_phai_co_trong_group_by(self, dashboard_request,
                                                               du_lieu_dashboard):
        _, queries = chay_dashboard(dashboard_request)
        for entry in queries:
            sql = entry["sql"]
            upper = sql.upper()
            start = upper.find("GROUP BY")
            if start == -1:
                continue
            order_at = upper.rfind("ORDER BY")
            if order_at <= start:
                continue
            group_clause, order_clause = sql[start:order_at], sql[order_at:]
            for table, column in COLUMN_RE.findall(order_clause):
                assert f'"{table}"."{column}"' in group_clause, (
                    f'Cột "{table}"."{column}" nằm trong ORDER BY nhưng không có trong '
                    f"GROUP BY — SQL Server sẽ báo lỗi 8127.\nSQL: {sql[:400]}"
                )

    def test_truy_van_gom_nhom_khong_mang_theo_ordering_mac_dinh(self, db):
        from django.db.models import Count

        from apps.orders.models import Order

        assert Order._meta.ordering == ["-created_at"]
        grouped = Order.objects.order_by().values("status").annotate(c=Count("id"))
        assert grouped.query.order_by == ()
        assert "ORDER BY" not in str(grouped.query).upper()


class TestTrangAdminMoDuoc:

    @pytest.mark.parametrize("url", [
        "/admin/",
        "/admin/accounts/address/",
        "/admin/catalog/product/",
        "/admin/inventory/stocktransaction/",
        "/admin/orders/order/",
        "/admin/content/banner/",
    ])
    def test_superuser_mo_duoc_moi_trang(self, client, superuser, url, du_lieu_dashboard):
        client.force_login(superuser)
        assert client.get(url).status_code == 200

    def test_trang_sua_don_hang(self, client, superuser, order):
        client.force_login(superuser)
        assert client.get(f"/admin/orders/order/{order.pk}/change/").status_code == 200
