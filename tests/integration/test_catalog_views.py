from decimal import Decimal

import pytest
from django.urls import reverse

from apps.catalog.models import Review

pytestmark = pytest.mark.django_db


@pytest.fixture
def catalog(product_factory, batch_factory, category, brand):
    from apps.catalog.models import Brand

    brand_khac = Brand.objects.create(name="Samsung")
    re_con_hang = product_factory(name="SSD 256GB", sku="SSD001", price=Decimal(800000))
    dat_het_hang = product_factory(name="SSD 2TB", sku="SSD002",
                                   price=Decimal(5000000), brand=brand_khac)
    batch_factory(re_con_hang, quantity=3, cost_price=600000)
    return {"re": re_con_hang, "dat": dat_het_hang, "brand_khac": brand_khac}


def ten_san_pham(response):
    return {p.name for p in response.context["products"]}


class TestLocSanPham:
    def test_tim_theo_tu_khoa(self, client, catalog):
        response = client.get(reverse("catalog:product_list"), {"q": "2TB"})
        assert ten_san_pham(response) == {"SSD 2TB"}

    def test_loc_theo_thuong_hieu(self, client, catalog, brand):
        response = client.get(reverse("catalog:product_list"), {"brand": brand.slug})
        assert ten_san_pham(response) == {"SSD 256GB"}

    def test_loc_theo_gia_toi_thieu(self, client, catalog):
        response = client.get(reverse("catalog:product_list"), {"min_price": 1000000})
        assert ten_san_pham(response) == {"SSD 2TB"}

    def test_loc_theo_gia_toi_da(self, client, catalog):
        response = client.get(reverse("catalog:product_list"), {"max_price": 1000000})
        assert ten_san_pham(response) == {"SSD 256GB"}

    def test_chi_hien_san_pham_con_hang(self, client, catalog):
        response = client.get(reverse("catalog:product_list"), {"in_stock": "1"})
        assert ten_san_pham(response) == {"SSD 256GB"}

    def test_chi_hien_san_pham_dang_giam_gia(self, client, catalog, product_factory):
        product_factory(name="RAM sale", sku="RAM111",
                        price=Decimal(2000000), sale_price=Decimal(1500000))
        response = client.get(reverse("catalog:product_list"), {"on_sale": "1"})
        assert ten_san_pham(response) == {"RAM sale"}

    def test_sap_xep_theo_gia_tang_dan(self, client, catalog):
        response = client.get(reverse("catalog:product_list"), {"sort": "price_asc"})
        assert [p.name for p in response.context["products"]] == ["SSD 256GB", "SSD 2TB"]

    def test_yeu_cau_htmx_chi_tra_ve_luoi_san_pham(self, client, catalog):
        response = client.get(reverse("catalog:product_list"), HTTP_HX_REQUEST="true")
        templates = [t.name for t in response.templates]
        assert "catalog/partials/product_grid.html" in templates
        assert "base.html" not in templates


class TestDanhGiaQuaHttp:
    def test_chua_dang_nhap_thi_khong_gui_duoc_danh_gia(self, client, product):
        response = client.post(
            reverse("catalog:review_create", args=[product.slug]),
            {"rating": 5, "content": "Tốt"},
        )
        assert response.status_code == 302
        assert Review.objects.count() == 0

    def test_tao_sua_xoa_danh_gia(self, client, customer, product):
        client.force_login(customer)

        client.post(reverse("catalog:review_create", args=[product.slug]),
                    {"rating": 4, "title": "Ổn", "content": "Chạy tốt"})
        review = Review.objects.get()
        assert review.rating == 4

        client.post(reverse("catalog:review_update", args=[review.pk]),
                    {"rating": 5, "title": "Rất ổn", "content": "Đã dùng 1 tháng"})
        review.refresh_from_db()
        assert review.rating == 5

        client.post(reverse("catalog:review_delete", args=[review.pk]))
        assert Review.objects.count() == 0

    def test_moi_nguoi_chi_danh_gia_mot_lan(self, client, customer, product):
        client.force_login(customer)
        for _ in range(2):
            client.post(reverse("catalog:review_create", args=[product.slug]),
                        {"rating": 5, "content": "Tốt"})
        assert Review.objects.filter(product=product, user=customer).count() == 1

    def test_khong_sua_duoc_danh_gia_cua_nguoi_khac(self, client, customer, other_customer, product):
        review = Review.objects.create(product=product, user=other_customer,
                                       rating=3, content="Bình thường")
        client.force_login(customer)
        response = client.post(reverse("catalog:review_update", args=[review.pk]),
                               {"rating": 1, "content": "Phá hoại"})
        assert response.status_code == 404
        review.refresh_from_db()
        assert review.rating == 3


class TestCacTrangCong:
    @pytest.mark.parametrize("url_name", [
        "core:home", "core:about", "core:contact",
        "catalog:product_list", "catalog:brand_list", "catalog:supplier_list",
        "content:news_list", "content:promotion_list",
    ])
    def test_trang_cong_mo_duoc(self, client, url_name, catalog):
        assert client.get(reverse(url_name)).status_code == 200

    def test_trang_chi_tiet_san_pham(self, client, product):
        assert client.get(product.get_absolute_url()).status_code == 200

    def test_luot_xem_tang_sau_moi_lan_xem(self, client, product):
        client.get(product.get_absolute_url())
        product.refresh_from_db()
        assert product.view_count == 1
