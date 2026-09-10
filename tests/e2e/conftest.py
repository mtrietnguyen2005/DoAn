"""GIAI ĐOẠN 2 — Cấu hình cho kiểm thử E2E bằng Playwright.

Điểm chính:

* ``live_server`` của pytest-django dựng một web server thật, Playwright
  điều khiển trình duyệt thật truy cập vào đó.
* Tự động chụp ảnh màn hình khi test gãy, lưu vào ``tests/e2e/screenshots/``.
* Chạy được cả chế độ Headless (mặc định) lẫn Headed (thêm cờ ``--headed``).
* Dữ liệu mẫu được tạo sẵn qua fixture để mỗi kịch bản đều bắt đầu từ
  trạng thái sạch và biết trước.
"""
import os

# Playwright (API đồng bộ) chạy bên trong một event loop riêng. Django phát hiện
# có event loop thì chặn mọi truy vấn đồng bộ để tránh treo. Cờ dưới đây cho phép
# các fixture tạo dữ liệu thật. Phải đặt TRƯỚC khi Django thực hiện truy vấn.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product, Supplier
from apps.inventory.models import Batch
from apps.orders.models import PromoCode

from .pages.admin_pages import AdminBatchPage, AdminDashboardPage, AdminLoginPage, AdminOrderPage
from .pages.auth_pages import LoginPage, RegisterPage
from .pages.cart_pages import CartPage, CheckoutPage
from .pages.order_pages import OrderDetailPage, OrderListPage
from .pages.product_pages import ProductDetailPage, ProductListPage

User = get_user_model()

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"

# Ghi chú: các test E2E phải dùng ``django_db(transaction=True)``. Web server do
# ``live_server`` dựng lên chạy ở luồng khác, nên dữ liệu nằm trong transaction
# chưa commit sẽ không được luồng đó nhìn thấy.


# ============================================================================
# TỰ ĐỘNG CHỤP ẢNH KHI TEST GÃY
# ============================================================================
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Gắn kết quả từng giai đoạn vào item để fixture bên dưới đọc được."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    """Chụp lại màn hình đúng thời điểm test thất bại.

    Ảnh giúp nhìn ngay ra trang đang ở trạng thái nào khi hỏng, thay vì
    phải đọc suông thông báo lỗi.
    """
    yield
    report = getattr(request.node, "report_call", None)
    if report is None or not report.failed:
        return
    page = request.node.funcargs.get("page")
    if page is None:
        return
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = request.node.name.replace("/", "_").replace("[", "_").replace("]", "")
    path = SCREENSHOT_DIR / f"{safe_name}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
        print(f"\n📸 Đã lưu ảnh màn hình lúc test gãy: {path}")
    except Exception as exc:  # trình duyệt có thể đã đóng
        print(f"\n⚠️ Không chụp được ảnh màn hình: {exc}")


# ============================================================================
# CHẶN TÀI NGUYÊN NGOÀI
# ============================================================================
#: Các máy chủ chỉ phục vụ phần trang trí (phông chữ, CSS). Chặn luôn cho nhanh
#: và để test không phụ thuộc vào mạng. Bộ test dùng selector ngữ nghĩa
#: (name, text) chứ không dựa vào CSS nên chặn cũng không ảnh hưởng.
COSMETIC_HOSTS = (
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.tailwindcss.com",
    "content-autofill.googleapis.com",
)


@pytest.fixture(autouse=True)
def block_external_requests(page, site_url):
    """Chặn bớt request ra Internet để test nhanh và ổn định.

    Mặc định chỉ chặn phông chữ và CSS. HTMX (từ cdnjs) **vẫn được tải** để
    kịch bản đi đúng luồng thật của người dùng.

    Đặt ``E2E_OFFLINE=1`` để chặn toàn bộ tài nguyên ngoài — dùng khi máy không
    có Internet hoặc trên máy chủ CI bị hạn chế mạng. Khi đó giao diện chạy ở
    chế độ dự phòng (form gửi theo cách thông thường thay vì qua HTMX), và các
    kịch bản vẫn phải chạy đúng.
    """
    offline = os.environ.get("E2E_OFFLINE") in ("1", "true", "True")

    def handler(route):
        url = route.request.url
        if url.startswith(site_url) or url.startswith(("data:", "about:", "blob:")):
            route.continue_()
        elif offline or any(host in url for host in COSMETIC_HOSTS):
            route.abort()
        else:
            route.continue_()

    page.route("**/*", handler)
    yield
    try:
        page.unroute("**/*", handler)
    except Exception:
        pass   # trang có thể đã đóng


# ============================================================================
# CẤU HÌNH TRÌNH DUYỆT
# ============================================================================
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Tuỳ chỉnh tham số khởi chạy trình duyệt.

    ``PLAYWRIGHT_CHROMIUM_PATH`` cho phép trỏ tới một bản Chromium đã cài sẵn
    trên máy chủ CI, thay vì bắt Playwright tải bản riêng.
    """
    args = {
        **browser_type_launch_args,
        "args": [
            "--disable-dev-shm-usage",
            "--no-sandbox",
            # Tắt các kết nối nền của Chromium (autofill, đồng bộ, cập nhật
            # thành phần...). Chúng không liên quan tới test nhưng làm chậm
            # đáng kể khi máy bị hạn chế mạng.
            "--disable-background-networking",
            "--disable-features=AutofillServerCommunication,OptimizationHints,MediaRouter",
            "--disable-sync",
            "--no-first-run",
            "--disable-extensions",
        ],
    }
    executable = os.environ.get("PLAYWRIGHT_CHROMIUM_PATH")
    if executable:
        args["executable_path"] = executable
    return args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Cỡ màn hình cố định để bố cục hiển thị nhất quán giữa các lần chạy."""
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "locale": "vi-VN",
        "timezone_id": "Asia/Ho_Chi_Minh",
    }


@pytest.fixture
def site_url(live_server):
    """Địa chỉ gốc của web server thật do pytest-django dựng lên.

    Không đặt tên là ``base_url`` để tránh đụng fixture cùng tên của
    plugin ``pytest-base-url`` (đi kèm pytest-playwright, phạm vi session).
    """
    return live_server.url


# ============================================================================
# DỮ LIỆU MẪU CHO CÁC KỊCH BẢN E2E
# ============================================================================
@pytest.fixture
def shop_data(transactional_db):
    """Dựng một cửa hàng nhỏ đủ để chạy hết các kịch bản.

    Trả về ``dict`` chứa các đối tượng để test khẳng định kết quả.
    """
    today = timezone.localdate()

    cpu = Category.objects.create(name="CPU", icon="🔲", display_order=1)
    vga = Category.objects.create(name="VGA", icon="🎮", display_order=2)
    intel = Brand.objects.create(name="Intel", country="Hoa Kỳ")
    asus = Brand.objects.create(name="ASUS", country="Đài Loan")
    supplier = Supplier.objects.create(name="Công ty Máy tính Sài Gòn")

    # Sản phẩm chính: rẻ, còn hàng, dùng cho luồng đặt hàng
    core_i5 = Product.objects.create(
        name="Intel Core i5-13400F", sku="CPU0001", category=cpu, brand=intel,
        supplier=supplier, price=Decimal(1500000),
        short_description="CPU 10 nhân 16 luồng cho game thủ.",
        specifications="Socket: LGA 1700\nSố nhân: 10\nTDP: 65W",
        is_featured=True,
    )
    batch_early = Batch.objects.create(
        product=core_i5, batch_code="LO-SOM", supplier=supplier,
        quantity_in=4, quantity_remaining=4, cost_price=Decimal(1000000),
        received_date=today - timedelta(days=30),
    )
    batch_late = Batch.objects.create(
        product=core_i5, batch_code="LO-MUON", supplier=supplier,
        quantity_in=10, quantity_remaining=10, cost_price=Decimal(1200000),
        received_date=today - timedelta(days=5),
    )

    # Sản phẩm đắt, đang giảm giá — dùng để kiểm tra bộ lọc
    rtx = Product.objects.create(
        name="ASUS Dual RTX 4060 OC", sku="VGA0001", category=vga, brand=asus,
        supplier=supplier, price=Decimal(8000000), sale_price=Decimal(7000000),
        short_description="Card đồ hoạ chơi game Full HD.",
    )
    Batch.objects.create(
        product=rtx, batch_code="LO-VGA", supplier=supplier,
        quantity_in=6, quantity_remaining=6, cost_price=Decimal(5500000),
        received_date=today - timedelta(days=10),
    )

    # Sản phẩm hết hàng — dùng để kiểm tra bộ lọc "còn hàng"
    het_hang = Product.objects.create(
        name="Intel Core i9-14900K", sku="CPU0009", category=cpu, brand=intel,
        supplier=supplier, price=Decimal(15000000),
    )

    promo = PromoCode.objects.create(
        code="GIAM10", discount_type=PromoCode.DiscountType.PERCENT,
        value=Decimal(10), max_discount=Decimal(500000),
        end_date=timezone.now() + timedelta(days=30),
    )

    return {
        "category_cpu": cpu, "category_vga": vga,
        "brand_intel": intel, "brand_asus": asus, "supplier": supplier,
        "product": core_i5, "product_sale": rtx, "product_out_of_stock": het_hang,
        "batch_early": batch_early, "batch_late": batch_late,
        "promo": promo,
    }


@pytest.fixture
def customer_account(transactional_db):
    """Tài khoản khách hàng có sẵn để đăng nhập nhanh."""
    password = "MatKhauManh!23"
    user = User.objects.create_user(
        username="khachhang", email="khach@test.vn", password=password,
        last_name="Nguyễn", first_name="Văn A", phone="0901234567",
    )
    user.raw_password = password
    return user


@pytest.fixture
def admin_account(transactional_db):
    """Tài khoản quản trị viên."""
    password = "MatKhauManh!23"
    user = User.objects.create_superuser(
        username="quantri", email="quantri@test.vn", password=password,
    )
    user.raw_password = password
    return user


# ============================================================================
# FIXTURE TRẢ VỀ PAGE OBJECT
# ============================================================================
@pytest.fixture
def register_page(page, site_url):
    return RegisterPage(page, site_url)


@pytest.fixture
def login_page(page, site_url):
    return LoginPage(page, site_url)


@pytest.fixture
def product_list_page(page, site_url):
    return ProductListPage(page, site_url)


@pytest.fixture
def cart_page(page, site_url):
    return CartPage(page, site_url)


@pytest.fixture
def checkout_page(page, site_url):
    return CheckoutPage(page, site_url)


@pytest.fixture
def order_list_page(page, site_url):
    return OrderListPage(page, site_url)


@pytest.fixture
def admin_login_page(page, site_url):
    return AdminLoginPage(page, site_url)


@pytest.fixture
def admin_dashboard_page(page, site_url):
    return AdminDashboardPage(page, site_url)


@pytest.fixture
def admin_batch_page(page, site_url):
    return AdminBatchPage(page, site_url)


@pytest.fixture
def admin_order_page(page, site_url):
    return AdminOrderPage(page, site_url)


@pytest.fixture
def logged_in_customer(login_page, customer_account):
    """Đăng nhập sẵn bằng giao diện thật rồi trả về tài khoản."""
    login_page.go().login(customer_account.username, customer_account.raw_password)
    login_page.expect_logged_in()
    return customer_account


@pytest.fixture
def logged_in_admin(admin_login_page, admin_account):
    """Đăng nhập sẵn vào trang quản trị."""
    dashboard = admin_login_page.go().login(admin_account.username, admin_account.raw_password)
    return dashboard
