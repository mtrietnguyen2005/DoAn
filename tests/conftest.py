"""Fixtures dùng chung cho toàn bộ bộ kiểm thử.

pytest-django tự động dọn dẹp database sau mỗi test: mỗi test chạy trong một
transaction riêng và được rollback khi kết thúc, nên các test hoàn toàn độc lập
với nhau và không cần tự tay xoá dữ liệu.
"""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import Address
from apps.catalog.models import Brand, Category, Product, Review, Supplier
from apps.content.models import Banner, News, Promotion
from apps.inventory.models import Batch
from apps.orders.models import Order, PromoCode

User = get_user_model()


def pytest_report_header(config):
    """In rõ bộ test đang chạy trên cấu hình và cơ sở dữ liệu nào.

    Giúp phát hiện ngay trường hợp test vô tình chạy trên SQL Server thật
    thay vì SQLite trong bộ nhớ.
    """
    from django.conf import settings

    db = settings.DATABASES["default"]
    engine = db["ENGINE"].rsplit(".", 1)[-1]
    return [
        f"settings: {settings.SETTINGS_MODULE}",
        f"database: {engine} -> {db['NAME']}",
    ]


# ============================================================================
# CẤU HÌNH CHUNG
# ============================================================================
@pytest.fixture(autouse=True)
def fast_password_hashing(settings):
    """Dùng thuật toán băm nhanh để test chạy nhanh hơn nhiều lần.

    Chỉ ảnh hưởng trong lúc test. Test kiểm tra cấu hình băm mật khẩu thật
    của production sẽ tự ghi đè lại thiết lập này.
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture(autouse=True)
def media_to_tmp(settings, tmp_path):
    """Ảnh upload trong test được ghi vào thư mục tạm, không đụng media/ thật."""
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def today():
    return timezone.localdate()


# ============================================================================
# NGƯỜI DÙNG
# ============================================================================
@pytest.fixture
def user_factory(db):
    """Tạo người dùng tuỳ ý: user_factory(username="abc", is_staff=True)."""
    counter = {"n": 0}

    def _make(username=None, password="MatKhauManh!23", **kwargs):
        counter["n"] += 1
        username = username or f"nguoidung{counter['n']}"
        kwargs.setdefault("email", f"{username}@test.vn")
        return User.objects.create_user(username=username, password=password, **kwargs)

    return _make


@pytest.fixture
def customer(user_factory):
    """Khách hàng thông thường."""
    return user_factory(username="khachhang", email="khach@test.vn", phone="0901234567")


@pytest.fixture
def other_customer(user_factory):
    """Khách hàng thứ hai — dùng để kiểm tra cách ly dữ liệu giữa các user."""
    return user_factory(username="khachhang_khac", email="khac@test.vn")


@pytest.fixture
def staff_user(user_factory):
    """Admin thường: có quyền vào trang quản trị nhưng KHÔNG phải superuser."""
    from django.contrib.auth.models import Permission

    user = user_factory(username="nhanvien", email="nhanvien@test.vn", is_staff=True)
    # Cấp toàn bộ permission của Django để chứng minh rằng thứ chặn họ
    # là ReadOnlyForStaffMixin, chứ không phải do thiếu quyền.
    user.user_permissions.set(Permission.objects.all())
    return user


@pytest.fixture
def superuser(db):
    """Superuser: toàn quyền trên mọi resource."""
    return User.objects.create_superuser(
        username="quantri", email="quantri@test.vn", password="MatKhauManh!23"
    )


@pytest.fixture
def address(customer):
    return Address.objects.create(
        user=customer, full_name="Nguyễn Văn A", phone="0901234567",
        province="TP.HCM", district="Quận 1", ward="Bến Nghé", street="12 Lê Lợi",
    )


# ============================================================================
# DANH MỤC SẢN PHẨM
# ============================================================================
@pytest.fixture
def category(db):
    return Category.objects.create(name="CPU - Bộ vi xử lý", icon="🔲")


@pytest.fixture
def brand(db):
    return Brand.objects.create(name="Intel", country="Hoa Kỳ")


@pytest.fixture
def supplier(db):
    return Supplier.objects.create(name="Công ty Máy tính Sài Gòn", phone="0283822111")


@pytest.fixture
def product_factory(db, category, brand, supplier):
    """Tạo sản phẩm tuỳ ý: product_factory(price=1000, sale_price=800)."""
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        kwargs.setdefault("name", f"Sản phẩm mẫu {counter['n']}")
        kwargs.setdefault("sku", f"SKU{counter['n']:04d}")
        kwargs.setdefault("category", category)
        kwargs.setdefault("brand", brand)
        kwargs.setdefault("supplier", supplier)
        kwargs.setdefault("price", Decimal(1500000))
        return Product.objects.create(**kwargs)

    return _make


@pytest.fixture
def product(product_factory):
    """Sản phẩm giá 1.500.000đ, CHƯA có lô hàng nào (tồn kho = 0)."""
    return product_factory(
        name="Intel Core i5-13400F", sku="CPU0001", price=Decimal(1500000),
        specifications="Socket: LGA 1700\nSố nhân: 10\nTDP: 65W",
    )


@pytest.fixture
def discounted_product(product_factory):
    """Sản phẩm 8.000.000đ đang giảm còn 7.000.000đ (giảm 12,5%)."""
    return product_factory(
        name="ASUS RTX 4060 OC", sku="VGA0001",
        price=Decimal(8000000), sale_price=Decimal(7000000),
    )


# ============================================================================
# KHO HÀNG — LÔ SẢN PHẨM
# ============================================================================
@pytest.fixture
def batch_factory(db):
    """Tạo lô hàng tuỳ ý cho một sản phẩm."""
    counter = {"n": 0}

    def _make(product, quantity=10, cost_price=1000000, received_days_ago=None, **kwargs):
        counter["n"] += 1
        kwargs.setdefault("batch_code", f"LO{counter['n']:04d}")
        kwargs.setdefault("quantity_in", quantity)
        kwargs.setdefault("quantity_remaining", quantity)
        kwargs.setdefault("cost_price", Decimal(cost_price))
        if received_days_ago is not None:
            kwargs.setdefault("received_date", timezone.localdate() - timedelta(days=received_days_ago))
        return Batch.objects.create(product=product, **kwargs)

    return _make


@pytest.fixture
def batch_early(product, batch_factory):
    """Lô A: nhập kho SỚM (30 ngày trước), 4 sản phẩm, giá vốn 1.000.000đ.

    Theo quy tắc FIFO thì lô này phải được xuất kho TRƯỚC.
    """
    return batch_factory(product, quantity=4, cost_price=1000000,
                         received_days_ago=30, batch_code="LO-SOM")


@pytest.fixture
def batch_late(product, batch_factory):
    """Lô B: nhập kho MUỘN (5 ngày trước), 10 sản phẩm, giá vốn 1.200.000đ."""
    return batch_factory(product, quantity=10, cost_price=1200000,
                         received_days_ago=5, batch_code="LO-MUON")


@pytest.fixture
def product_with_batches(product, batch_early, batch_late):
    """Sản phẩm có tổng tồn kho 14 (4 từ lô sớm + 10 từ lô muộn)."""
    return product


# ============================================================================
# MÃ GIẢM GIÁ
# ============================================================================
@pytest.fixture
def promo_percent(db):
    """Giảm 10%, tối đa 500.000đ, không yêu cầu giá trị đơn tối thiểu."""
    return PromoCode.objects.create(
        code="GIAM10", discount_type=PromoCode.DiscountType.PERCENT,
        value=Decimal(10), max_discount=Decimal(500000),
        end_date=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def promo_fixed(db):
    """Giảm thẳng 200.000đ cho đơn từ 5.000.000đ."""
    return PromoCode.objects.create(
        code="GIAM200K", discount_type=PromoCode.DiscountType.FIXED,
        value=Decimal(200000), min_order_value=Decimal(5000000),
        end_date=timezone.now() + timedelta(days=30),
    )


@pytest.fixture
def promo_expired(db):
    """Mã đã hết hạn từ hôm qua."""
    return PromoCode.objects.create(
        code="HETHAN", discount_type=PromoCode.DiscountType.PERCENT, value=Decimal(50),
        start_date=timezone.now() - timedelta(days=10),
        end_date=timezone.now() - timedelta(days=1),
    )


# ============================================================================
# GIỎ HÀNG & ĐƠN HÀNG
# ============================================================================
class StubCart:
    """Giỏ hàng giả lập, chỉ cần đủ giao diện mà ``create_order`` sử dụng.

    Nhờ vậy test service đặt hàng không phụ thuộc vào session của HTTP request.
    """

    def __init__(self, items):
        self._items = items
        self.cleared = False

    def get_items(self):
        return self._items

    def clear(self):
        self.cleared = True


@pytest.fixture
def cart_factory():
    """Tạo giỏ hàng giả lập: cart_factory((product, 2), (product2, 1))."""

    def _make(*pairs):
        items = []
        for product, quantity in pairs:
            unit_price = product.final_price
            items.append({
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
                "stock": product.stock_quantity,
            })
        return StubCart(items)

    return _make


@pytest.fixture
def order_factory(customer, cart_factory):
    """Tạo đơn hàng thật thông qua service (có trừ kho, ghi COGS, ghi lịch sử)."""
    from apps.orders.services import create_order

    def _make(product, quantity=1, user=None, promo=None, **kwargs):
        kwargs.setdefault("receiver_name", "Nguyễn Văn A")
        kwargs.setdefault("receiver_phone", "0901234567")
        kwargs.setdefault("shipping_address", "12 Lê Lợi, Bến Nghé, Quận 1, TP.HCM")
        return create_order(
            user=user or customer,
            cart=cart_factory((product, quantity)),
            promo=promo,
            **kwargs,
        )

    return _make


@pytest.fixture
def order(product_with_batches, order_factory):
    """Đơn hàng 2 sản phẩm, lấy toàn bộ từ lô sớm (giá vốn 1.000.000đ)."""
    return order_factory(product_with_batches, quantity=2)


# ============================================================================
# NỘI DUNG
# ============================================================================
@pytest.fixture
def news_article(superuser):
    return News.objects.create(
        title="Hướng dẫn chọn CPU 2025", summary="Bài viết mẫu.",
        content="Nội dung bài viết.", author=superuser,
    )


@pytest.fixture
def promotion(db, discounted_product):
    promo = Promotion.objects.create(
        title="Đại tiệc linh kiện", discount_percent=20,
        end_date=timezone.now() + timedelta(days=15),
    )
    promo.products.add(discounted_product)
    return promo


@pytest.fixture
def review(product, customer):
    return Review.objects.create(
        product=product, user=customer, rating=5,
        title="Rất tốt", content="Sản phẩm chạy ổn định.",
    )
