"""GIAI ĐOẠN 2 — Kịch bản E2E luồng quản trị viên.

Luồng: Đăng nhập /admin → Thêm lô hàng mới → Duyệt trạng thái đơn
→ Kiểm tra thống kê trên Dashboard.
"""
import pytest
from django.utils import timezone
from playwright.sync_api import expect

from apps.inventory.models import Batch, StockTransaction
from apps.orders.models import Order, OrderStatusHistory

pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.fixture
def don_hang_cho_duyet(shop_data, customer_account):
    """Một đơn hàng ở trạng thái Chờ xác nhận để admin thao tác."""
    from apps.orders.services import create_order

    class _Cart:
        def __init__(self, items):
            self._items = items

        def get_items(self):
            return self._items

        def clear(self):
            pass

    product = shop_data["product"]
    cart = _Cart([{
        "product": product, "quantity": 2,
        "unit_price": product.final_price,
        "line_total": product.final_price * 2,
        "stock": product.stock_quantity,
    }])
    return create_order(
        user=customer_account, cart=cart,
        receiver_name="Nguyễn Văn A", receiver_phone="0901234567",
        shipping_address="12 Lê Lợi, Bến Nghé, Quận 1, TP.HCM",
    )


class TestDangNhapAdmin:
    def test_dang_nhap_admin_thanh_cong(self, admin_login_page, admin_account):
        dashboard = admin_login_page.go().login(
            admin_account.username, admin_account.raw_password)
        dashboard.expect_loaded()

    def test_sai_mat_khau_khong_vao_duoc(self, admin_login_page, admin_account):
        admin_login_page.go().login(admin_account.username, "mat-khau-sai")
        admin_login_page.expect_url_contains("/admin/login")

    def test_khach_hang_thuong_khong_vao_duoc_admin(self, admin_login_page, customer_account):
        """Tài khoản không phải staff bị giữ lại ở trang đăng nhập."""
        admin_login_page.go().login(customer_account.username, customer_account.raw_password)
        admin_login_page.expect_url_contains("/admin/login")


class TestQuanLyLoHang:
    def test_them_lo_hang_moi_va_ghi_vet_nhap_kho(self, admin_batch_page, shop_data,
                                                  logged_in_admin):
        today = timezone.localdate()
        ton_kho_truoc = shop_data["product"].stock_quantity

        admin_batch_page.go_add().create_batch(
            batch_code="LO-MOI-E2E",
            product_sku=shop_data["product"].sku,
            quantity=25,
            cost_price=950000,
            received_date=today.strftime("%Y-%m-%d"),
        )

        lo_moi = Batch.objects.get(batch_code="LO-MOI-E2E")
        assert lo_moi.quantity_in == 25
        assert lo_moi.quantity_remaining == 25   # tự điền bằng số lượng nhập

        # Tồn kho của sản phẩm tăng đúng
        shop_data["product"].refresh_from_db()
        assert shop_data["product"].stock_quantity == ton_kho_truoc + 25

        # Có ghi vết giao dịch nhập kho
        giao_dich = StockTransaction.objects.get(
            batch=lo_moi, transaction_type=StockTransaction.Type.IN)
        assert giao_dich.quantity == 25
        assert giao_dich.created_by.is_superuser

    def test_lo_hang_moi_hien_trong_danh_sach(self, admin_batch_page, shop_data,
                                              logged_in_admin):
        admin_batch_page.go()
        assert admin_batch_page.find_row("LO-SOM").count() == 1
        assert admin_batch_page.find_row("LO-MUON").count() == 1


class TestDuyetTrangThaiDonHang:
    def test_doi_trang_thai_don_va_ghi_lich_su(self, admin_order_page, don_hang_cho_duyet,
                                               logged_in_admin):
        admin_order_page.go().open_order(don_hang_cho_duyet.code)
        assert admin_order_page.current_status() == "pending"

        admin_order_page.change_status("confirmed")

        don_hang_cho_duyet.refresh_from_db()
        assert don_hang_cho_duyet.status == Order.Status.CONFIRMED

        # Lịch sử được ghi thêm một dòng (ban đầu 1 dòng "Chờ xác nhận")
        lich_su = list(don_hang_cho_duyet.status_history.values_list("to_status", flat=True))
        assert lich_su == ["pending", "confirmed"]
        assert OrderStatusHistory.objects.filter(
            order=don_hang_cho_duyet, to_status="confirmed").first().changed_by.is_superuser

    def test_duyet_qua_nhieu_trang_thai_den_hoan_thanh(self, admin_order_page,
                                                       don_hang_cho_duyet, logged_in_admin):
        for trang_thai in ("confirmed", "shipping", "completed"):
            admin_order_page.go().open_order(don_hang_cho_duyet.code)
            admin_order_page.change_status(trang_thai)

        don_hang_cho_duyet.refresh_from_db()
        assert don_hang_cho_duyet.status == Order.Status.COMPLETED
        assert don_hang_cho_duyet.completed_at is not None
        assert list(don_hang_cho_duyet.status_history.values_list("to_status", flat=True)) == [
            "pending", "confirmed", "shipping", "completed",
        ]

    def test_admin_huy_don_thi_kho_duoc_hoan_dung_lo(self, admin_order_page, shop_data,
                                                     don_hang_cho_duyet, logged_in_admin):
        shop_data["batch_early"].refresh_from_db()
        assert shop_data["batch_early"].quantity_remaining == 2   # đã trừ 2

        admin_order_page.go().open_order(don_hang_cho_duyet.code)
        admin_order_page.change_status("cancelled")

        shop_data["batch_early"].refresh_from_db()
        shop_data["batch_late"].refresh_from_db()
        assert shop_data["batch_early"].quantity_remaining == 4    # hoàn đúng lô
        assert shop_data["batch_late"].quantity_remaining == 10

        don_hang_cho_duyet.refresh_from_db()
        assert don_hang_cho_duyet.status == Order.Status.CANCELLED


class TestDashboardThongKe:
    """Độ đúng của số liệu (tổng sản phẩm, đếm theo trạng thái, cảnh báo tồn
    kho) đã được kiểm thử chi tiết ở tầng tích hợp
    (``tests/integration/test_dashboard.py::TestDashboard``, đọc thẳng
    context trả về, không qua trình duyệt). Ở tầng E2E chỉ giữ lại hai ca:
    xác nhận giao diện thật render đúng, và ca chặn tái phát lỗi SQL Server
    thật sự từng xảy ra trên chính trang này."""

    def test_dashboard_hien_du_bon_the_thong_ke(self, admin_dashboard_page, shop_data,
                                                don_hang_cho_duyet, logged_in_admin):
        admin_dashboard_page.go().expect_loaded()
        for tieu_de in ("Người dùng", "Sản phẩm", "Đơn hàng", "Đánh giá"):
            admin_dashboard_page.expect_text_visible(tieu_de)

    def test_dashboard_mo_duoc_tren_sql_server(self, admin_dashboard_page, don_hang_cho_duyet,
                                               logged_in_admin):
        """Chặn tái phát lỗi 8127 (ORDER BY không nằm trong GROUP BY).

        Trang này từng không mở được trên SQL Server. Chạy bộ test với
        ``TEST_ON_MSSQL=True`` sẽ kiểm chứng lại trên đúng CSDL thật.
        """
        admin_dashboard_page.go().expect_loaded()
        assert admin_dashboard_page.revenue_text()
        assert admin_dashboard_page.profit_text()


class TestPhanQuyenReadOnlyTrenGiaoDien:
    """Admin thường chỉ xem được 3 resource nhạy cảm, không có nút Thêm."""

    @pytest.fixture
    def nhan_vien(self, transactional_db):
        from django.contrib.auth import get_user_model
        from django.contrib.auth.models import Permission

        User = get_user_model()
        password = "MatKhauManh!23"
        user = User.objects.create_user(
            username="nhanvien", email="nv@test.vn", password=password, is_staff=True)
        user.user_permissions.set(Permission.objects.all())
        user.raw_password = password
        return user

    @pytest.mark.parametrize("duong_dan", [
        "/admin/accounts/address/",
        "/admin/catalog/review/",
        "/admin/inventory/stocktransaction/",
    ])
    def test_khong_co_nut_them_moi(self, admin_login_page, page, site_url,
                                   nhan_vien, duong_dan):
        admin_login_page.go().login(nhan_vien.username, nhan_vien.raw_password)
        page.goto(f"{site_url}{duong_dan}", wait_until="domcontentloaded")

        # Trang xem được, nhưng không có liên kết "Thêm"
        assert "/admin/login" not in page.url
        assert page.locator("a.addlink, a[href$='/add/']").count() == 0

    def test_van_them_duoc_san_pham(self, admin_login_page, page, site_url, nhan_vien):
        admin_login_page.go().login(nhan_vien.username, nhan_vien.raw_password)
        page.goto(f"{site_url}/admin/catalog/product/add/", wait_until="domcontentloaded")
        assert page.locator("input[name='sku']").count() == 1
