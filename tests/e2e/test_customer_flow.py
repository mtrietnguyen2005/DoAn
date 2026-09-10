"""GIAI ĐOẠN 2 — Kịch bản E2E luồng khách hàng.

Luồng đầy đủ: Đăng ký → Đăng nhập → Lọc sản phẩm → Thêm giỏ hàng
→ Đặt hàng → Xem lịch sử → Huỷ đơn hợp lệ.

Toàn bộ thao tác đi qua Page Object, không có selector rải rác trong test.
"""
import pytest
from playwright.sync_api import expect

from apps.orders.models import Order

from .pages.order_pages import OrderDetailPage

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


class TestDangKyVaDangNhap:
    def test_dang_ky_tai_khoan_moi_thanh_cong(self, register_page, shop_data):
        register_page.go().register(
            username="nguoimoi", email="nguoimoi@test.vn",
            password="MatKhauManh!23", last_name="Trần", first_name="Bình",
            phone="0987654321",
        )
        # Đăng ký xong được đăng nhập luôn và chuyển về trang chủ
        expect(register_page.page).to_have_url(register_page.base_url + "/")
        register_page.expect_text_visible("Trần Bình")

    def test_dang_ky_that_bai_khi_email_da_ton_tai(self, register_page, customer_account):
        register_page.go().register(
            username="nguoikhac", email=customer_account.email, password="MatKhauManh!23",
        ).expect_field_error("đã được sử dụng")

    def test_dang_nhap_bang_ten_dang_nhap(self, login_page, customer_account):
        login_page.go().login(customer_account.username, customer_account.raw_password)
        login_page.expect_logged_in()

    def test_dang_nhap_bang_email(self, login_page, customer_account):
        login_page.go().login(customer_account.email, customer_account.raw_password)
        login_page.expect_logged_in()

    def test_dang_nhap_sai_mat_khau_bao_loi(self, login_page, customer_account):
        login_page.go().login(customer_account.username, "mat-khau-sai") \
            .expect_error("không đúng")


class TestTimKiemVaLocSanPham:
    """Logic lọc/sắp xếp đã được kiểm thử đầy đủ ở tầng tích hợp
    (``tests/integration/test_catalog_views.py::TestLocSanPham``, 8 ca qua
    HTTP trực tiếp). Ở tầng E2E chỉ cần xác nhận một lượt tìm kiếm đại diện
    hoạt động đúng qua giao diện thật, không lặp lại toàn bộ ma trận lọc."""

    def test_hien_thi_toan_bo_san_pham(self, product_list_page, shop_data):
        product_list_page.go().expect_product_count(3)

    def test_tim_kiem_theo_tu_khoa(self, product_list_page, shop_data):
        product_list_page.go().search("RTX").expect_product_names(["ASUS Dual RTX 4060 OC"])

    def test_khong_tim_thay_thi_hien_thong_bao(self, product_list_page, shop_data):
        product_list_page.go().search("khong-ton-tai-san-pham-nay")
        product_list_page.expect_empty_result()


class TestGioHang:
    def test_them_san_pham_vao_gio_tu_trang_danh_sach(self, product_list_page, shop_data):
        product_list_page.go()
        assert product_list_page.cart_count() == 0

        product_list_page.add_first_product_to_cart()
        expect(product_list_page.cart_badge).to_have_text("1")

    def test_them_san_pham_voi_so_luong_tuy_chon(self, page, site_url, shop_data):
        from .pages.product_pages import ProductDetailPage

        detail = ProductDetailPage(page, site_url, slug=shop_data["product"].slug)
        detail.go().set_quantity(3).add_to_cart()
        expect(detail.cart_badge).to_have_text("3")

    def test_tang_giam_so_luong_trong_gio(self, product_list_page, cart_page, shop_data):
        product_list_page.go().add_first_product_to_cart()
        cart_page.go().expect_first_item_quantity(1)
        cart_page.increase_first_item().expect_first_item_quantity(2)
        cart_page.decrease_first_item().expect_first_item_quantity(1)

    def test_xoa_san_pham_khoi_gio(self, product_list_page, cart_page, shop_data):
        product_list_page.go().add_first_product_to_cart()
        cart_page.go().remove_first_item().expect_empty()

    def test_ap_dung_ma_giam_gia(self, page, site_url, cart_page, shop_data):
        from .pages.product_pages import ProductDetailPage

        # Mua 2 sản phẩm 1.5 triệu = 3 triệu, giảm 10% = 300.000đ
        ProductDetailPage(page, site_url, slug=shop_data["product"].slug).go() \
            .set_quantity(2).add_to_cart()
        cart_page.go().apply_promo("GIAM10").expect_discount_contains("300.000")

    def test_ma_giam_gia_khong_ton_tai_bao_loi(self, product_list_page, cart_page, shop_data):
        product_list_page.go().add_first_product_to_cart()
        cart_page.go().apply_promo("MA-KHONG-CO-THAT").expect_promo_error("không tồn tại")


class TestDatHangVaHuyDon:
    """Kịch bản trọng tâm: đặt hàng thật rồi huỷ, kiểm tra hoàn kho."""

    def _dat_hang(self, page, site_url, cart_page, shop_data, quantity=2):
        from .pages.product_pages import ProductDetailPage

        ProductDetailPage(page, site_url, slug=shop_data["product"].slug).go() \
            .set_quantity(quantity).add_to_cart()
        checkout = cart_page.go().go_to_checkout()
        checkout.fill_receiver(
            name="Nguyễn Văn A", phone="0901234567", province="TP.HCM",
            district="Quận 1", ward="Bến Nghé", street="12 Lê Lợi",
            note="Giao giờ hành chính",
        )
        return checkout.place_order()

    def test_dat_hang_thanh_cong(self, page, site_url, cart_page, shop_data, logged_in_customer):
        success = self._dat_hang(page, site_url, cart_page, shop_data)
        success.expect_success()

        code = success.order_code()
        assert code.startswith("DH")

        order = Order.objects.get(code=code)
        assert order.user == logged_in_customer
        assert order.status == Order.Status.PENDING
        assert order.receiver_name == "Nguyễn Văn A"
        assert order.customer_note == "Giao giờ hành chính"

    def test_dat_hang_lam_giam_ton_kho_dung_lo(self, page, site_url, cart_page,
                                               shop_data, logged_in_customer):
        """Lô nhập kho sớm phải bị trừ trước (FIFO)."""
        self._dat_hang(page, site_url, cart_page, shop_data, quantity=2)

        shop_data["batch_early"].refresh_from_db()
        shop_data["batch_late"].refresh_from_db()
        assert shop_data["batch_early"].quantity_remaining == 2   # 4 - 2
        assert shop_data["batch_late"].quantity_remaining == 10   # chưa đụng tới

    def test_gio_hang_duoc_xoa_sau_khi_dat(self, page, site_url, cart_page,
                                           shop_data, logged_in_customer):
        self._dat_hang(page, site_url, cart_page, shop_data)
        cart_page.go().expect_empty()

    def test_xem_lich_su_don_hang(self, page, site_url, cart_page, order_list_page,
                                  shop_data, logged_in_customer):
        success = self._dat_hang(page, site_url, cart_page, shop_data)
        code = success.order_code()

        order_list_page.go()
        assert code in order_list_page.order_codes()

    def test_xem_chi_tiet_don_va_lich_su_trang_thai(self, page, site_url, cart_page,
                                                    shop_data, logged_in_customer):
        success = self._dat_hang(page, site_url, cart_page, shop_data)
        detail = success.view_order_detail()

        detail.expect_status("Chờ xác nhận")
        assert "Chờ xác nhận" in detail.status_history()

    def test_huy_don_hop_le_va_hoan_kho(self, page, site_url, cart_page,
                                        shop_data, logged_in_customer):
        """Huỷ đơn ở trạng thái Chờ xác nhận: được phép, và kho phải hoàn đúng lô."""
        success = self._dat_hang(page, site_url, cart_page, shop_data, quantity=2)
        code = success.order_code()

        shop_data["batch_early"].refresh_from_db()
        assert shop_data["batch_early"].quantity_remaining == 2

        detail = OrderDetailPage(page, site_url, code=code).go()
        assert detail.can_cancel() is True

        detail.cancel_order("Đổi ý không mua nữa")
        detail.expect_cancelled()

        # Kho được hoàn về đúng lô ban đầu
        shop_data["batch_early"].refresh_from_db()
        shop_data["batch_late"].refresh_from_db()
        assert shop_data["batch_early"].quantity_remaining == 4
        assert shop_data["batch_late"].quantity_remaining == 10

        order = Order.objects.get(code=code)
        assert order.status == Order.Status.CANCELLED

    def test_khong_cho_huy_don_dang_giao(self, page, site_url, cart_page,
                                         shop_data, logged_in_customer):
        from apps.orders.services import change_order_status

        success = self._dat_hang(page, site_url, cart_page, shop_data)
        order = Order.objects.get(code=success.order_code())
        change_order_status(order, Order.Status.CONFIRMED)
        change_order_status(order, Order.Status.SHIPPING)

        detail = OrderDetailPage(page, site_url, code=order.code).go()
        assert detail.can_cancel() is False
        assert detail.shipping_blocked_notice() is True


class TestDanhGiaSanPham:
    def test_viet_sua_va_xoa_danh_gia(self, page, site_url, shop_data, logged_in_customer):
        from apps.catalog.models import Review
        from .pages.product_pages import ProductDetailPage

        detail = ProductDetailPage(page, site_url, slug=shop_data["product"].slug)
        detail.go().write_review(rating=4, content="Sản phẩm chạy ổn định.", title="Khá tốt")

        detail.expect_my_review_contains("Khá tốt")

        review = Review.objects.get(product=shop_data["product"], user=logged_in_customer)
        assert review.rating == 4

        detail.go().delete_my_review()
        detail.expect_no_my_review()
        assert not Review.objects.filter(pk=review.pk).exists()

    def test_khach_chua_dang_nhap_khong_viet_duoc_danh_gia(self, page, site_url, shop_data):
        from .pages.product_pages import ProductDetailPage

        detail = ProductDetailPage(page, site_url, slug=shop_data["product"].slug).go()
        detail.expect_text_visible("để viết đánh giá")
