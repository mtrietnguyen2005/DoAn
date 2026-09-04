"""Kiểm thử tài khoản, phiên đăng nhập và địa chỉ nhận hàng."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Address

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="khachhang", email="khach@test.vn", password="matkhau123"
        )

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "nguoimoi", "email": "moi@test.vn", "last_name": "Trần", "first_name": "Bình",
            "phone": "0900000001", "password1": "MatKhauManh!23", "password2": "MatKhauManh!23",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="nguoimoi").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_rejects_duplicate_email(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "nguoimoi2", "email": "khach@test.vn",
            "password1": "MatKhauManh!23", "password2": "MatKhauManh!23",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="nguoimoi2").exists())

    def test_login_with_username(self):
        self.assertTrue(self.client.login(username="khachhang", password="matkhau123"))

    def test_login_with_email(self):
        response = self.client.post(reverse("accounts:login"),
                                    {"username": "khach@test.vn", "password": "matkhau123"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_fails_with_wrong_password(self):
        self.client.post(reverse("accounts:login"), {"username": "khachhang", "password": "sai"})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_session_expires_at_browser_close_when_not_remembered(self):
        self.client.post(reverse("accounts:login"),
                         {"username": "khachhang", "password": "matkhau123"})
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_remember_me_keeps_session(self):
        self.client.post(reverse("accounts:login"),
                         {"username": "khachhang", "password": "matkhau123", "remember_me": "on"})
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.client.post(reverse("accounts:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)


class AddressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="khach", email="k@test.vn", password="matkhau123")
        self.client.force_login(self.user)

    def _create(self, name="Nguyễn Văn A", default=False):
        data = {"full_name": name, "phone": "0900000000", "province": "TP.HCM",
                "district": "Quận 1", "ward": "Bến Nghé", "street": "1 Lê Lợi"}
        if default:
            data["is_default"] = "on"
        return self.client.post(reverse("accounts:address_create"), data)

    def test_first_address_becomes_default(self):
        self._create()
        self.assertTrue(Address.objects.get().is_default)

    def test_only_one_default_address(self):
        self._create("Người A", default=True)
        self._create("Người B", default=True)
        self.assertEqual(Address.objects.filter(is_default=True).count(), 1)
        self.assertEqual(Address.objects.get(is_default=True).full_name, "Người B")

    def test_set_default_address(self):
        self._create("Người A", default=True)
        self._create("Người B")
        address_a = Address.objects.get(full_name="Người A")
        self.client.post(reverse("accounts:address_set_default", args=[address_a.pk]))
        address_a.refresh_from_db()
        self.assertTrue(address_a.is_default)

    def test_delete_address(self):
        self._create()
        address = Address.objects.get()
        self.client.post(reverse("accounts:address_delete", args=[address.pk]))
        self.assertEqual(Address.objects.count(), 0)

    def test_cannot_touch_other_users_address(self):
        other = User.objects.create_user(username="khac", email="kh@test.vn", password="matkhau123")
        address = Address.objects.create(user=other, full_name="Người khác", phone="0900000009",
                                         province="HN", district="Ba Đình", ward="Cống Vị", street="1 Đội Cấn")
        response = self.client.post(reverse("accounts:address_delete", args=[address.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Address.objects.filter(pk=address.pk).exists())

    def test_full_address_property(self):
        self._create()
        self.assertEqual(Address.objects.get().full_address, "1 Lê Lợi, Bến Nghé, Quận 1, TP.HCM")
