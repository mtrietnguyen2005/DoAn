import re
from pathlib import Path

import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db

DAU_HIEU_LOI = ("{#", "#}", "{%", "%}", "{{", "}}")

TEMPLATE_DIR = Path(settings.BASE_DIR) / "templates"


@pytest.mark.integration
class TestGhiChuTemplate:

    def test_khong_co_ghi_chu_mot_dau_trai_nhieu_dong(self):
        loi = []
        for tep in sorted(TEMPLATE_DIR.rglob("*.html")):
            noi_dung = tep.read_text(encoding="utf-8")
            for khop in re.finditer(r"\{#(.*?)#\}", noi_dung, re.S):
                if "\n" in khop.group(1):
                    dong = noi_dung[: khop.start()].count("\n") + 1
                    loi.append(f"{tep.relative_to(TEMPLATE_DIR)}:{dong}")
        assert not loi, (
            "Ghi chú {# #} trải nhiều dòng sẽ hiện ra trang web như văn bản.\n"
            "Hãy đổi sang {% comment %} ... {% endcomment %} tại:\n  "
            + "\n  ".join(loi)
        )


@pytest.mark.integration
class TestTrangKhongLoMaNguon:

    def _kiem_tra(self, response, ten_trang):
        html = response.content.decode()
        khong_script = re.sub(r"<script.*?</script>", "", html, flags=re.S)
        for dau_hieu in DAU_HIEU_LOI:
            assert dau_hieu not in khong_script, (
                f"Trang {ten_trang} lộ cú pháp template '{dau_hieu}' ra HTML — "
                "nhiều khả năng do ghi chú {# #} trải nhiều dòng."
            )

    @pytest.mark.parametrize("url_name", [
        "core:home", "core:about", "core:contact",
        "catalog:product_list", "catalog:brand_list", "catalog:supplier_list",
        "content:news_list", "content:promotion_list",
        "orders:cart_detail", "accounts:login", "accounts:register",
    ])
    def test_trang_cong(self, client, url_name, product_with_batches):
        url = reverse(url_name)
        self._kiem_tra(client.get(url), url)

    def test_trang_chi_tiet_san_pham(self, client, product_with_batches):
        self._kiem_tra(client.get(product_with_batches.get_absolute_url()),
                       "chi tiết sản phẩm")

    def test_trang_gio_hang_co_san_pham(self, client, product_with_batches):
        client.post(reverse("orders:cart_add", args=[product_with_batches.pk]),
                    {"quantity": 2})
        self._kiem_tra(client.get(reverse("orders:cart_detail")), "giỏ hàng")

    def test_trang_thanh_toan(self, client, customer, product_with_batches):
        client.force_login(customer)
        client.post(reverse("orders:cart_add", args=[product_with_batches.pk]),
                    {"quantity": 1})
        self._kiem_tra(client.get(reverse("orders:checkout")), "thanh toán")

    def test_trang_don_hang(self, client, customer, order):
        client.force_login(customer)
        self._kiem_tra(client.get(reverse("orders:order_list")), "danh sách đơn")
        self._kiem_tra(client.get(reverse("orders:order_detail", args=[order.code])),
                       "chi tiết đơn")

    def test_trang_tai_khoan(self, client, customer, address):
        client.force_login(customer)
        for url_name in ("accounts:profile", "accounts:address_list",
                         "accounts:my_reviews", "accounts:password_change"):
            url = reverse(url_name)
            self._kiem_tra(client.get(url), url)
