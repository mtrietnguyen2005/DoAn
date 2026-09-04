"""Kiểm thử tích hợp: luồng xác thực qua HTTP (không cần trình duyệt)."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.models import Address

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.mark.accounts
class TestDangKy:
    def test_dang_ky_tao_tai_khoan_va_dang_nhap_luon(self, client):
        response = client.post(reverse("accounts:register"), {
            "username": "nguoimoi", "email": "moi@test.vn",
            "last_name": "Trần", "first_name": "Bình", "phone": "0900000001",
            "password1": "MatKhauManh!23", "password2": "MatKhauManh!23",
        })
        assert response.status_code == 302
        assert User.objects.filter(username="nguoimoi").exists()
        assert "_auth_user_id" in client.session

    def test_tu_choi_email_da_ton_tai(self, client, customer):
        response = client.post(reverse("accounts:register"), {
            "username": "nguoimoi2", "email": customer.email,
            "password1": "MatKhauManh!23", "password2": "MatKhauManh!23",
        })
        assert response.status_code == 200
        assert not User.objects.filter(username="nguoimoi2").exists()

    def test_tu_choi_mat_khau_khong_khop(self, client):
        response = client.post(reverse("accounts:register"), {
            "username": "nguoimoi3", "email": "moi3@test.vn",
            "password1": "MatKhauManh!23", "password2": "MatKhauKhac!99",
        })
        assert response.status_code == 200
        assert not User.objects.filter(username="nguoimoi3").exists()


@pytest.mark.accounts
class TestDangNhapVaPhien:
    def test_dang_nhap_bang_ten_dang_nhap(self, client, customer):
        assert client.login(username=customer.username, password="MatKhauManh!23")

    def test_dang_nhap_bang_email(self, client, customer):
        response = client.post(reverse("accounts:login"),
                               {"username": customer.email, "password": "MatKhauManh!23"})
        assert response.status_code == 302
        assert "_auth_user_id" in client.session

    def test_sai_mat_khau_thi_khong_vao_duoc(self, client, customer):
        client.post(reverse("accounts:login"),
                    {"username": customer.username, "password": "sai-mat-khau"})
        assert "_auth_user_id" not in client.session

    def test_khong_ghi_nho_thi_phien_het_khi_dong_trinh_duyet(self, client, customer):
        client.post(reverse("accounts:login"),
                    {"username": customer.username, "password": "MatKhauManh!23"})
        assert client.session.get_expire_at_browser_close() is True

    def test_ghi_nho_dang_nhap_thi_giu_phien(self, client, customer):
        client.post(reverse("accounts:login"), {
            "username": customer.username, "password": "MatKhauManh!23", "remember_me": "on",
        })
        assert client.session.get_expire_at_browser_close() is False

    def test_dang_xuat_bat_buoc_dung_phuong_thuc_post(self, client, customer):
        client.force_login(customer)
        assert client.get(reverse("accounts:logout")).status_code == 405
        client.post(reverse("accounts:logout"))
        assert "_auth_user_id" not in client.session

    def test_trang_ho_so_yeu_cau_dang_nhap(self, client):
        response = client.get(reverse("accounts:profile"))
        assert response.status_code == 302
        assert reverse("accounts:login") in response.url


@pytest.mark.accounts
class TestDiaChiQuaHttp:
    def _tao(self, client, name="Nguyễn Văn A", mac_dinh=False):
        data = {"full_name": name, "phone": "0900000000", "province": "TP.HCM",
                "district": "Quận 1", "ward": "Bến Nghé", "street": "1 Lê Lợi"}
        if mac_dinh:
            data["is_default"] = "on"
        return client.post(reverse("accounts:address_create"), data)

    def test_them_dia_chi(self, client, customer):
        client.force_login(customer)
        self._tao(client)
        assert Address.objects.filter(user=customer).count() == 1

    def test_dat_lam_dia_chi_mac_dinh(self, client, customer):
        client.force_login(customer)
        self._tao(client, "Người A", mac_dinh=True)
        self._tao(client, "Người B")
        nguoi_b = Address.objects.get(full_name="Người B")

        client.post(reverse("accounts:address_set_default", args=[nguoi_b.pk]))

        nguoi_b.refresh_from_db()
        assert nguoi_b.is_default is True
        assert Address.objects.filter(user=customer, is_default=True).count() == 1

    def test_xoa_dia_chi(self, client, customer, address):
        client.force_login(customer)
        client.post(reverse("accounts:address_delete", args=[address.pk]))
        assert not Address.objects.filter(pk=address.pk).exists()

    def test_khong_dung_duoc_dia_chi_cua_nguoi_khac(self, client, customer, other_customer):
        khac = Address.objects.create(
            user=other_customer, full_name="Người khác", phone="0900000009",
            province="Hà Nội", district="Ba Đình", ward="Cống Vị", street="1 Đội Cấn",
        )
        client.force_login(customer)
        assert client.post(reverse("accounts:address_delete", args=[khac.pk])).status_code == 404
        assert Address.objects.filter(pk=khac.pk).exists()
