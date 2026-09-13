from decimal import Decimal

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def product_ban(product_factory, batch_factory):
    p = product_factory(name="Ryzen 5", sku="CPU100",
                        price=Decimal(5000000), sale_price=Decimal(4500000))
    batch_factory(p, quantity=5, cost_price=3800000)
    return p


class TestGioHang:
    def test_them_vao_gio(self, client, product_ban):
        response = client.post(reverse("orders:cart_add", args=[product_ban.pk]),
                               {"quantity": 2}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.json()["count"] == 2

    def test_gio_hang_dung_gia_khuyen_mai(self, client, product_ban):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 2})
        response = client.get(reverse("orders:cart_detail"))
        assert response.context["subtotal"] == Decimal(9000000)

    def test_so_luong_bi_chan_boi_ton_kho(self, client, product_ban):
        response = client.post(reverse("orders:cart_add", args=[product_ban.pk]),
                               {"quantity": 99}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.json()["count"] == 5

    def test_cap_nhat_va_xoa_khoi_gio(self, client, product_ban):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 3})
        client.post(reverse("orders:cart_update", args=[product_ban.pk]),
                    {"quantity": 1}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert client.get(reverse("orders:cart_count")).json()["count"] == 1

        client.post(reverse("orders:cart_remove", args=[product_ban.pk]),
                    HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert client.get(reverse("orders:cart_count")).json()["count"] == 0

    def test_xoa_toan_bo_gio_hang(self, client, product_ban):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 2})
        client.post(reverse("orders:cart_clear"))
        assert client.get(reverse("orders:cart_count")).json()["count"] == 0

    def test_dong_bo_gio_hang_tu_localstorage(self, client, product_ban):
        response = client.post(
            reverse("orders:cart_sync"),
            data='{"items": {"%s": 2}}' % product_ban.pk,
            content_type="application/json",
        )
        assert response.json()["count"] == 2

    def test_gio_hang_duoc_giu_sau_khi_dang_nhap(self, client, product_ban, customer):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 2})
        client.login(username=customer.username, password="MatKhauManh!23")
        assert client.get(reverse("orders:cart_count")).json()["count"] == 2

    def test_khong_them_duoc_san_pham_het_hang(self, client, product):
        response = client.post(reverse("orders:cart_add", args=[product.pk]),
                               {"quantity": 1}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        assert response.json()["ok"] is False


class TestMaGiamGiaQuaHttp:
    def test_ap_dung_ma_hop_le(self, client, product_ban, promo_percent):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 1})
        client.post(reverse("orders:promo_apply"), {"code": promo_percent.code})
        response = client.get(reverse("orders:cart_detail"))
        assert response.context["discount"] == Decimal(450000)

    def test_go_ma_giam_gia(self, client, product_ban, promo_percent):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 1})
        client.post(reverse("orders:promo_apply"), {"code": promo_percent.code})
        client.post(reverse("orders:promo_remove"))
        response = client.get(reverse("orders:cart_detail"))
        assert response.context["discount"] == 0

    def test_ma_het_han_bi_tu_choi(self, client, product_ban, promo_expired):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 1})
        client.post(reverse("orders:promo_apply"), {"code": promo_expired.code})
        response = client.get(reverse("orders:cart_detail"))
        assert response.context["discount"] == 0


class TestDatHangQuaHttp:
    def test_thanh_toan_yeu_cau_dang_nhap(self, client, product_ban):
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 1})
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url

    def test_gio_rong_thi_khong_vao_duoc_trang_thanh_toan(self, client, customer):
        client.force_login(customer)
        response = client.get(reverse("orders:checkout"))
        assert response.status_code == 302

    def test_dat_hang_thanh_cong_qua_http(self, client, customer, product_ban):
        from apps.orders.models import Order

        client.force_login(customer)
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 2})
        client.post(reverse("orders:checkout"), {
            "receiver_name": "Nguyễn Văn A", "receiver_phone": "0912345678",
            "receiver_email": "a@test.vn", "province": "TP.HCM", "district": "Quận 1",
            "ward": "Bến Nghé", "street": "12 Lê Lợi", "payment_method": "cod",
        }, follow=True)

        order = Order.objects.get()
        assert order.user == customer
        assert order.total_quantity == 2
        product_ban.refresh_from_db()
        assert product_ban.stock_quantity == 3

    def test_so_dien_thoai_khong_hop_le_bi_tu_choi(self, client, customer, product_ban):
        from apps.orders.models import Order

        client.force_login(customer)
        client.post(reverse("orders:cart_add", args=[product_ban.pk]), {"quantity": 1})
        response = client.post(reverse("orders:checkout"), {
            "receiver_name": "A", "receiver_phone": "abc", "province": "TP.HCM",
            "district": "Quận 1", "ward": "Bến Nghé", "street": "1 Lê Lợi",
            "payment_method": "cod",
        })
        assert response.status_code == 200
        assert Order.objects.count() == 0

    def test_huy_don_qua_http(self, client, customer, order):
        from apps.orders.models import Order

        client.force_login(customer)
        client.post(reverse("orders:order_cancel", args=[order.code]), {"reason": "Đổi ý"})
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    def test_khong_xem_duoc_don_cua_nguoi_khac(self, client, other_customer, order):
        client.force_login(other_customer)
        response = client.get(reverse("orders:order_detail", args=[order.code]))
        assert response.status_code == 404


@pytest.mark.integration
class TestCsrfChoKhachVangLai:

    def test_trang_cong_luon_phat_hanh_csrf_token(self, client, product_ban):
        for url in (reverse("core:home"), reverse("catalog:product_list")):
            response = client.get(url)
            assert 'name="csrf-token"' in response.content.decode(), url
            assert "csrftoken" in response.cookies or "csrftoken" in client.cookies, url

    def test_khach_vang_lai_them_duoc_vao_gio_khi_bat_kiem_tra_csrf(self, product_ban):
        from django.test import Client

        strict = Client(enforce_csrf_checks=True)
        page = strict.get(reverse("catalog:product_list"))

        html = page.content.decode()
        token = html.split('name="csrf-token" content="')[1].split('"')[0]
        assert token

        response = strict.post(
            reverse("orders:cart_add", args=[product_ban.pk]),
            {"quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_CSRFTOKEN=token,
        )
        assert response.status_code == 200, "Bị chặn CSRF - khách vãng lai không mua được"
        assert response.json()["count"] == 1

    def test_thieu_token_thi_bi_chan(self, product_ban):
        from django.test import Client

        strict = Client(enforce_csrf_checks=True)
        response = strict.post(
            reverse("orders:cart_add", args=[product_ban.pk]),
            {"quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 403
