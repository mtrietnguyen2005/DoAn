from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.inventory.models import Batch


class PromoCode(models.Model):

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Giảm theo phần trăm"
        FIXED = "fixed", "Giảm số tiền cố định"

    code = models.CharField("Mã giảm giá", max_length=40, unique=True)
    description = models.CharField("Mô tả", max_length=255, blank=True)
    discount_type = models.CharField(
        "Kiểu giảm giá", max_length=10, choices=DiscountType.choices, default=DiscountType.PERCENT
    )
    value = models.DecimalField("Giá trị giảm", max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    max_discount = models.DecimalField(
        "Giảm tối đa", max_digits=12, decimal_places=0, null=True, blank=True,
        help_text="Chỉ áp dụng cho kiểu giảm theo phần trăm",
    )
    min_order_value = models.DecimalField("Giá trị đơn tối thiểu", max_digits=12, decimal_places=0, default=0)
    start_date = models.DateTimeField("Ngày bắt đầu", default=timezone.now)
    end_date = models.DateTimeField("Ngày kết thúc")
    usage_limit = models.PositiveIntegerField("Số lượt sử dụng tối đa", default=0, help_text="0 = không giới hạn")
    used_count = models.PositiveIntegerField("Đã sử dụng", default=0)
    is_active = models.BooleanField("Đang hoạt động", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Mã giảm giá"
        verbose_name_plural = "Mã giảm giá"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        now = timezone.now()
        if not self.is_active or not (self.start_date <= now <= self.end_date):
            return False
        return self.usage_limit == 0 or self.used_count < self.usage_limit

    def error_for(self, subtotal):
        now = timezone.now()
        if not self.is_active:
            return "Mã giảm giá đã bị vô hiệu hóa."
        if now < self.start_date:
            return "Mã giảm giá chưa đến thời gian sử dụng."
        if now > self.end_date:
            return "Mã giảm giá đã hết hạn."
        if self.usage_limit and self.used_count >= self.usage_limit:
            return "Mã giảm giá đã hết lượt sử dụng."
        if subtotal < self.min_order_value:
            return f"Đơn hàng tối thiểu {self.min_order_value:,.0f}đ mới dùng được mã này."
        return None

    def calculate_discount(self, subtotal) -> Decimal:
        subtotal = Decimal(subtotal)
        if self.discount_type == self.DiscountType.PERCENT:
            discount = subtotal * self.value / Decimal(100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.value
        return Decimal(int(min(discount, subtotal)))


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Chờ xác nhận"
        CONFIRMED = "confirmed", "Đã xác nhận"
        SHIPPING = "shipping", "Đang giao"
        COMPLETED = "completed", "Hoàn thành"
        CANCELLED = "cancelled", "Đã hủy"

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Thanh toán khi nhận hàng (COD)"

    CANCELLABLE_STATUSES = {Status.PENDING, Status.CONFIRMED}
    STOCK_DEDUCTED_STATUSES = {Status.PENDING, Status.CONFIRMED, Status.SHIPPING, Status.COMPLETED}

    code = models.CharField("Mã đơn hàng", max_length=30, unique=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="Khách hàng",
    )

    receiver_name = models.CharField("Họ tên người nhận", max_length=120)
    receiver_phone = models.CharField("Số điện thoại", max_length=20)
    receiver_email = models.EmailField("Email", blank=True)
    shipping_address = models.CharField("Địa chỉ giao hàng", max_length=500)

    subtotal = models.DecimalField("Tạm tính", max_digits=14, decimal_places=0, default=0)
    shipping_fee = models.DecimalField("Phí vận chuyển", max_digits=12, decimal_places=0, default=0)
    discount_amount = models.DecimalField("Số tiền giảm", max_digits=12, decimal_places=0, default=0)
    total = models.DecimalField("Tổng thanh toán", max_digits=14, decimal_places=0, default=0)

    promo_code = models.ForeignKey(
        PromoCode, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="orders", verbose_name="Mã giảm giá",
    )
    payment_method = models.CharField(
        "Hình thức thanh toán", max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.COD
    )
    status = models.CharField("Trạng thái", max_length=20, choices=Status.choices, default=Status.PENDING)
    customer_note = models.TextField("Ghi chú của khách", blank=True)
    admin_note = models.TextField("Ghi chú nội bộ", blank=True)

    created_at = models.DateTimeField("Ngày đặt", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật", auto_now=True)
    completed_at = models.DateTimeField("Ngày hoàn thành", null=True, blank=True)
    cancelled_at = models.DateTimeField("Ngày hủy", null=True, blank=True)

    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return self.code or f"Đơn hàng #{self.pk}"

    def save(self, *args, **kwargs):
        creating = self._state.adding
        super().save(*args, **kwargs)
        if creating and not self.code:
            self.code = f"DH{timezone.localtime(self.created_at):%y%m%d}{self.pk:05d}"
            super().save(update_fields=["code"])

    @property
    def can_cancel(self):
        return self.status in self.CANCELLABLE_STATUSES

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_cost(self):
        return sum(item.cost_price * item.quantity for item in self.items.all())

    @property
    def profit(self):
        return self.subtotal - self.total_cost - self.discount_amount

    @property
    def status_color(self):
        return {
            self.Status.PENDING: "amber",
            self.Status.CONFIRMED: "blue",
            self.Status.SHIPPING: "indigo",
            self.Status.COMPLETED: "emerald",
            self.Status.CANCELLED: "rose",
        }.get(self.status, "slate")


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Đơn hàng")
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name="order_items", verbose_name="Sản phẩm"
    )
    product_name = models.CharField("Tên sản phẩm", max_length=255)
    product_sku = models.CharField("Mã SKU", max_length=60, blank=True)
    unit_price = models.DecimalField("Đơn giá bán", max_digits=12, decimal_places=0)
    cost_price = models.DecimalField(
        "Giá vốn (COGS)", max_digits=12, decimal_places=0, default=0,
        help_text="Giá vốn bình quân tại thời điểm bán, dùng để tính lợi nhuận",
    )
    quantity = models.PositiveIntegerField("Số lượng", validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def line_cost(self):
        return self.cost_price * self.quantity

    @property
    def line_profit(self):
        return self.line_total - self.line_cost


class OrderItemBatch(models.Model):

    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="batch_allocations", verbose_name="Chi tiết đơn"
    )
    batch = models.ForeignKey(
        Batch, on_delete=models.PROTECT, related_name="order_allocations", verbose_name="Lô hàng"
    )
    quantity = models.PositiveIntegerField("Số lượng lấy từ lô")
    cost_price = models.DecimalField("Giá vốn của lô", max_digits=12, decimal_places=0)
    is_returned = models.BooleanField("Đã hoàn kho", default=False)

    class Meta:
        verbose_name = "Phân bổ lô hàng"
        verbose_name_plural = "Phân bổ lô hàng"

    def __str__(self):
        return f"{self.batch.batch_code} × {self.quantity}"


class OrderStatusHistory(models.Model):

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history", verbose_name="Đơn hàng"
    )
    from_status = models.CharField("Trạng thái cũ", max_length=20, choices=Order.Status.choices, blank=True)
    to_status = models.CharField("Trạng thái mới", max_length=20, choices=Order.Status.choices)
    note = models.CharField("Ghi chú", max_length=255, blank=True)
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="order_status_changes", verbose_name="Người thay đổi",
    )
    created_at = models.DateTimeField("Thời điểm", auto_now_add=True)

    class Meta:
        verbose_name = "Lịch sử trạng thái đơn"
        verbose_name_plural = "Lịch sử trạng thái đơn"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.order.code}: {self.from_status or '—'} → {self.to_status}"


class Shipping(models.Model):

    class Carrier(models.TextChoices):
        GHTK = "ghtk", "Giao Hàng Tiết Kiệm"
        GHN = "ghn", "Giao Hàng Nhanh"
        VNPOST = "vnpost", "Viettel Post"
        SELF = "self", "Shop tự giao"

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="shipping", verbose_name="Đơn hàng"
    )
    carrier = models.CharField("Đơn vị vận chuyển", max_length=20, choices=Carrier.choices, default=Carrier.GHTK)
    tracking_code = models.CharField("Mã vận đơn", max_length=80, blank=True)
    fee = models.DecimalField("Phí vận chuyển", max_digits=12, decimal_places=0, default=0)
    estimated_date = models.DateField("Dự kiến giao", null=True, blank=True)
    shipped_at = models.DateTimeField("Thời điểm bàn giao", null=True, blank=True)
    delivered_at = models.DateTimeField("Thời điểm giao thành công", null=True, blank=True)
    note = models.CharField("Ghi chú", max_length=255, blank=True)

    class Meta:
        verbose_name = "Vận chuyển"
        verbose_name_plural = "Vận chuyển"

    def __str__(self):
        return f"Vận chuyển đơn {self.order.code}"
