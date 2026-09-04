from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Product, Supplier


class Batch(models.Model):
    """Lô hàng nhập kho. Tồn kho của sản phẩm = tổng số lượng còn lại của các lô."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="batches", verbose_name="Sản phẩm")
    batch_code = models.CharField("Mã lô", max_length=60, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="batches", verbose_name="Nhà cung cấp",
    )
    quantity_in = models.PositiveIntegerField("Số lượng nhập", validators=[MinValueValidator(1)])
    quantity_remaining = models.PositiveIntegerField("Số lượng còn lại", default=0)
    cost_price = models.DecimalField(
        "Giá vốn / đơn vị", max_digits=12, decimal_places=0, validators=[MinValueValidator(0)]
    )
    received_date = models.DateField("Ngày nhập kho", default=timezone.localdate)
    manufacture_date = models.DateField("Ngày sản xuất", null=True, blank=True)
    expiry_date = models.DateField(
        "Hạn sử dụng / hết bảo hành lô", null=True, blank=True,
        help_text="Dùng để cảnh báo lô hàng sắp hết hạn",
    )
    note = models.CharField("Ghi chú", max_length=255, blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Lô hàng"
        verbose_name_plural = "Lô hàng"
        ordering = ["expiry_date", "received_date", "id"]
        indexes = [models.Index(fields=["product", "quantity_remaining"])]

    def __str__(self):
        return f"{self.batch_code} · {self.product.name} (còn {self.quantity_remaining})"

    def clean(self):
        if self.quantity_remaining > self.quantity_in:
            raise ValidationError({"quantity_remaining": "Số lượng còn lại không được lớn hơn số lượng nhập."})
        if self.expiry_date and self.manufacture_date and self.expiry_date < self.manufacture_date:
            raise ValidationError({"expiry_date": "Hạn sử dụng phải sau ngày sản xuất."})

    @property
    def quantity_sold(self):
        return self.quantity_in - self.quantity_remaining

    @property
    def is_expired(self):
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())

    @property
    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days

    @property
    def total_cost(self):
        return self.cost_price * self.quantity_in


class StockTransaction(models.Model):
    """Lịch sử giao dịch kho: nhập, xuất, điều chỉnh, hoàn trả."""

    class Type(models.TextChoices):
        IN = "in", "Nhập kho"
        OUT = "out", "Xuất kho (bán hàng)"
        RETURN = "return", "Hoàn trả (hủy đơn)"
        ADJUST = "adjust", "Điều chỉnh thủ công"

    batch = models.ForeignKey(
        Batch, on_delete=models.CASCADE, related_name="transactions", verbose_name="Lô hàng"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_transactions", verbose_name="Sản phẩm"
    )
    transaction_type = models.CharField("Loại giao dịch", max_length=10, choices=Type.choices)
    quantity = models.IntegerField("Số lượng", help_text="Dương = tăng tồn, âm = giảm tồn")
    quantity_after = models.IntegerField("Tồn lô sau giao dịch", default=0)
    reference = models.CharField("Chứng từ liên quan", max_length=100, blank=True)
    note = models.CharField("Ghi chú", max_length=255, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="stock_transactions", verbose_name="Người thực hiện",
    )
    created_at = models.DateTimeField("Thời điểm", auto_now_add=True)

    class Meta:
        verbose_name = "Giao dịch kho"
        verbose_name_plural = "Giao dịch kho"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["product", "-created_at"])]

    def __str__(self):
        return f"{self.get_transaction_type_display()} {self.quantity:+d} · {self.batch.batch_code}"
