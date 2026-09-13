import os

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



@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"report_{report.when}", report)


@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
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
    except Exception as exc:
        print(f"\n⚠️ Không chụp được ảnh màn hình: {exc}")


COSMETIC_HOSTS = (
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdn.tailwindcss.com",
    "content-autofill.googleapis.com",
)


@pytest.fixture(autouse=True)
def block_external_requests(page, site_url):
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
        pass


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    args = {
        **browser_type_launch_args,
        "args": [
            "--disable-dev-shm-usage",
            "--no-sandbox",
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
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        "locale": "vi-VN",
        "timezone_id": "Asia/Ho_Chi_Minh",
    }


@pytest.fixture
def site_url(live_server):
    return live_server.url


@pytest.fixture
def shop_data(transactional_db):
    today = timezone.localdate()

    cpu = Category.objects.create(name="CPU", icon="🔲", display_order=1)
    vga = Category.objects.create(name="VGA", icon="🎮", display_order=2)
    intel = Brand.objects.create(name="Intel", country="Hoa Kỳ")
    asus = Brand.objects.create(name="ASUS", country="Đài Loan")
    supplier = Supplier.objects.create(name="Công ty Máy tính Sài Gòn")

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
    password = "MatKhauManh!23"
    user = User.objects.create_user(
        username="khachhang", email="khach@test.vn", password=password,
        last_name="Nguyễn", first_name="Văn A", phone="0901234567",
    )
    user.raw_password = password
    return user


@pytest.fixture
def admin_account(transactional_db):
    password = "MatKhauManh!23"
    user = User.objects.create_superuser(
        username="quantri", email="quantri@test.vn", password=password,
    )
    user.raw_password = password
    return user


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
    login_page.go().login(customer_account.username, customer_account.raw_password)
    login_page.expect_logged_in()
    return customer_account


@pytest.fixture
def logged_in_admin(admin_login_page, admin_account):
    dashboard = admin_login_page.go().login(admin_account.username, admin_account.raw_password)
    return dashboard
