
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
        ("inventory", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PromoCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        max_length=40, unique=True, verbose_name="Mã giảm giá"
                    ),
                ),
                (
                    "description",
                    models.CharField(blank=True, max_length=255, verbose_name="Mô tả"),
                ),
                (
                    "discount_type",
                    models.CharField(
                        choices=[
                            ("percent", "Giảm theo phần trăm"),
                            ("fixed", "Giảm số tiền cố định"),
                        ],
                        default="percent",
                        max_length=10,
                        verbose_name="Kiểu giảm giá",
                    ),
                ),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=0,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Giá trị giảm",
                    ),
                ),
                (
                    "max_discount",
                    models.DecimalField(
                        blank=True,
                        decimal_places=0,
                        help_text="Chỉ áp dụng cho kiểu giảm theo phần trăm",
                        max_digits=12,
                        null=True,
                        verbose_name="Giảm tối đa",
                    ),
                ),
                (
                    "min_order_value",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        max_digits=12,
                        verbose_name="Giá trị đơn tối thiểu",
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Ngày bắt đầu"
                    ),
                ),
                ("end_date", models.DateTimeField(verbose_name="Ngày kết thúc")),
                (
                    "usage_limit",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="0 = không giới hạn",
                        verbose_name="Số lượt sử dụng tối đa",
                    ),
                ),
                (
                    "used_count",
                    models.PositiveIntegerField(default=0, verbose_name="Đã sử dụng"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Đang hoạt động"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo"),
                ),
            ],
            options={
                "verbose_name": "Mã giảm giá",
                "verbose_name_plural": "Mã giảm giá",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        blank=True,
                        max_length=30,
                        unique=True,
                        verbose_name="Mã đơn hàng",
                    ),
                ),
                (
                    "receiver_name",
                    models.CharField(max_length=120, verbose_name="Họ tên người nhận"),
                ),
                (
                    "receiver_phone",
                    models.CharField(max_length=20, verbose_name="Số điện thoại"),
                ),
                (
                    "receiver_email",
                    models.EmailField(blank=True, max_length=254, verbose_name="Email"),
                ),
                (
                    "shipping_address",
                    models.CharField(max_length=500, verbose_name="Địa chỉ giao hàng"),
                ),
                (
                    "subtotal",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        max_digits=14,
                        verbose_name="Tạm tính",
                    ),
                ),
                (
                    "shipping_fee",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        max_digits=12,
                        verbose_name="Phí vận chuyển",
                    ),
                ),
                (
                    "discount_amount",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        max_digits=12,
                        verbose_name="Số tiền giảm",
                    ),
                ),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        max_digits=14,
                        verbose_name="Tổng thanh toán",
                    ),
                ),
                (
                    "payment_method",
                    models.CharField(
                        choices=[("cod", "Thanh toán khi nhận hàng (COD)")],
                        default="cod",
                        max_length=20,
                        verbose_name="Hình thức thanh toán",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Chờ xác nhận"),
                            ("confirmed", "Đã xác nhận"),
                            ("shipping", "Đang giao"),
                            ("completed", "Hoàn thành"),
                            ("cancelled", "Đã hủy"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Trạng thái",
                    ),
                ),
                (
                    "customer_note",
                    models.TextField(blank=True, verbose_name="Ghi chú của khách"),
                ),
                (
                    "admin_note",
                    models.TextField(blank=True, verbose_name="Ghi chú nội bộ"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Ngày đặt"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Cập nhật"),
                ),
                (
                    "completed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Ngày hoàn thành"
                    ),
                ),
                (
                    "cancelled_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Ngày hủy"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Khách hàng",
                    ),
                ),
                (
                    "promo_code",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="orders.promocode",
                        verbose_name="Mã giảm giá",
                    ),
                ),
            ],
            options={
                "verbose_name": "Đơn hàng",
                "verbose_name_plural": "Đơn hàng",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "product_name",
                    models.CharField(max_length=255, verbose_name="Tên sản phẩm"),
                ),
                (
                    "product_sku",
                    models.CharField(blank=True, max_length=60, verbose_name="Mã SKU"),
                ),
                (
                    "unit_price",
                    models.DecimalField(
                        decimal_places=0, max_digits=12, verbose_name="Đơn giá bán"
                    ),
                ),
                (
                    "cost_price",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        help_text="Giá vốn bình quân tại thời điểm bán, dùng để tính lợi nhuận",
                        max_digits=12,
                        verbose_name="Giá vốn (COGS)",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="Số lượng",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="orders.order",
                        verbose_name="Đơn hàng",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="order_items",
                        to="catalog.product",
                        verbose_name="Sản phẩm",
                    ),
                ),
            ],
            options={
                "verbose_name": "Chi tiết đơn hàng",
                "verbose_name_plural": "Chi tiết đơn hàng",
            },
        ),
        migrations.CreateModel(
            name="OrderItemBatch",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.PositiveIntegerField(verbose_name="Số lượng lấy từ lô"),
                ),
                (
                    "cost_price",
                    models.DecimalField(
                        decimal_places=0, max_digits=12, verbose_name="Giá vốn của lô"
                    ),
                ),
                (
                    "is_returned",
                    models.BooleanField(default=False, verbose_name="Đã hoàn kho"),
                ),
                (
                    "batch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="order_allocations",
                        to="inventory.batch",
                        verbose_name="Lô hàng",
                    ),
                ),
                (
                    "order_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="batch_allocations",
                        to="orders.orderitem",
                        verbose_name="Chi tiết đơn",
                    ),
                ),
            ],
            options={
                "verbose_name": "Phân bổ lô hàng",
                "verbose_name_plural": "Phân bổ lô hàng",
            },
        ),
        migrations.CreateModel(
            name="OrderStatusHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "from_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending", "Chờ xác nhận"),
                            ("confirmed", "Đã xác nhận"),
                            ("shipping", "Đang giao"),
                            ("completed", "Hoàn thành"),
                            ("cancelled", "Đã hủy"),
                        ],
                        max_length=20,
                        verbose_name="Trạng thái cũ",
                    ),
                ),
                (
                    "to_status",
                    models.CharField(
                        choices=[
                            ("pending", "Chờ xác nhận"),
                            ("confirmed", "Đã xác nhận"),
                            ("shipping", "Đang giao"),
                            ("completed", "Hoàn thành"),
                            ("cancelled", "Đã hủy"),
                        ],
                        max_length=20,
                        verbose_name="Trạng thái mới",
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Ghi chú"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Thời điểm"),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="order_status_changes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người thay đổi",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="orders.order",
                        verbose_name="Đơn hàng",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lịch sử trạng thái đơn",
                "verbose_name_plural": "Lịch sử trạng thái đơn",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="Shipping",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "carrier",
                    models.CharField(
                        choices=[
                            ("ghtk", "Giao Hàng Tiết Kiệm"),
                            ("ghn", "Giao Hàng Nhanh"),
                            ("vnpost", "Viettel Post"),
                            ("self", "Shop tự giao"),
                        ],
                        default="ghtk",
                        max_length=20,
                        verbose_name="Đơn vị vận chuyển",
                    ),
                ),
                (
                    "tracking_code",
                    models.CharField(
                        blank=True, max_length=80, verbose_name="Mã vận đơn"
                    ),
                ),
                (
                    "fee",
                    models.DecimalField(
                        decimal_places=0,
                        default=0,
                        max_digits=12,
                        verbose_name="Phí vận chuyển",
                    ),
                ),
                (
                    "estimated_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Dự kiến giao"
                    ),
                ),
                (
                    "shipped_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Thời điểm bàn giao"
                    ),
                ),
                (
                    "delivered_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Thời điểm giao thành công"
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Ghi chú"
                    ),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipping",
                        to="orders.order",
                        verbose_name="Đơn hàng",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vận chuyển",
                "verbose_name_plural": "Vận chuyển",
            },
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["code"], name="orders_orde_code_77e86c_idx"),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["status", "-created_at"], name="orders_orde_status_079368_idx"
            ),
        ),
    ]
