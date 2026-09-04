from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, Sum
from django.urls import reverse
from django.utils.text import slugify

from apps.accounts.models import User


def unique_slug(instance, value, field_name="slug"):
    """Sinh slug duy nhất từ chuỗi đầu vào."""
    base = slugify(value, allow_unicode=False) or "muc"
    model = instance.__class__
    slug, index = base, 2
    while model.objects.filter(**{field_name: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug


class Category(models.Model):
    """Danh mục linh kiện: CPU, VGA, RAM, Mainboard, Laptop..."""

    name = models.CharField("Tên danh mục", max_length=120)
    slug = models.SlugField("Đường dẫn", max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", verbose_name="Danh mục cha",
    )
    description = models.TextField("Mô tả", blank=True)
    image = models.ImageField("Ảnh", upload_to="categories/", blank=True, null=True)
    icon = models.CharField("Icon (emoji hoặc tên icon)", max_length=50, blank=True)
    display_order = models.PositiveIntegerField("Thứ tự hiển thị", default=0)
    is_active = models.BooleanField("Đang hoạt động", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ["display_order", "name"]

    def __str__(self):
        return f"{self.parent.name} › {self.name}" if self.parent else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_list") + f"?category={self.slug}"

    @property
    def product_count(self):
        return self.products.filter(is_active=True).count()


class Brand(models.Model):
    """Thương hiệu: Intel, AMD, ASUS, MSI, Kingston..."""

    name = models.CharField("Tên thương hiệu", max_length=120, unique=True)
    slug = models.SlugField("Đường dẫn", max_length=140, unique=True, blank=True)
    logo = models.ImageField("Logo", upload_to="brands/", blank=True, null=True)
    country = models.CharField("Quốc gia", max_length=80, blank=True)
    website = models.URLField("Website", blank=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang hoạt động", default=True)

    class Meta:
        verbose_name = "Thương hiệu"
        verbose_name_plural = "Thương hiệu"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Supplier(models.Model):
    """Nhà cung cấp hàng hoá."""

    name = models.CharField("Tên nhà cung cấp", max_length=160)
    slug = models.SlugField("Đường dẫn", max_length=180, unique=True, blank=True)
    contact_person = models.CharField("Người liên hệ", max_length=120, blank=True)
    phone = models.CharField("Số điện thoại", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.CharField("Địa chỉ", max_length=255, blank=True)
    tax_code = models.CharField("Mã số thuế", max_length=50, blank=True)
    logo = models.ImageField("Logo", upload_to="suppliers/", blank=True, null=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang hợp tác", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_stock(self):
        return self.annotate(
            stock=Sum("batches__quantity_remaining"),
            review_avg=Avg("reviews__rating"),
            review_count=Count("reviews", distinct=True),
        )


class Product(models.Model):
    """Sản phẩm / linh kiện."""

    name = models.CharField("Tên sản phẩm", max_length=255)
    slug = models.SlugField("Đường dẫn", max_length=280, unique=True, blank=True)
    sku = models.CharField("Mã SKU", max_length=60, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Danh mục"
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.PROTECT, related_name="products", verbose_name="Thương hiệu"
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="products", verbose_name="Nhà cung cấp",
    )
    short_description = models.CharField("Mô tả ngắn", max_length=300, blank=True)
    description = models.TextField("Mô tả chi tiết", blank=True)
    specifications = models.TextField(
        "Thông số kỹ thuật", blank=True,
        help_text="Mỗi dòng một thông số theo dạng: Tên thông số: Giá trị",
    )
    price = models.DecimalField("Giá bán", max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField(
        "Giá khuyến mãi", max_digits=12, decimal_places=0, null=True, blank=True,
        validators=[MinValueValidator(0)], help_text="Để trống nếu không giảm giá",
    )
    warranty_months = models.PositiveIntegerField("Bảo hành (tháng)", default=12)
    weight_gram = models.PositiveIntegerField("Khối lượng (gram)", default=0)
    thumbnail = models.ImageField("Ảnh đại diện", upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField("Đang kinh doanh", default=True)
    is_featured = models.BooleanField("Sản phẩm nổi bật", default=False)
    view_count = models.PositiveIntegerField("Lượt xem", default=0)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật lần cuối", auto_now=True)

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["is_active", "is_featured"]),
        ]

    def __str__(self):
        return f"[{self.sku}] {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    # ---- Giá ----
    @property
    def final_price(self) -> Decimal:
        """Giá thực bán (ưu tiên giá khuyến mãi)."""
        if self.sale_price and self.sale_price < self.price:
            return self.sale_price
        return self.price

    @property
    def has_discount(self) -> bool:
        return bool(self.sale_price and self.sale_price < self.price)

    @property
    def discount_percent(self) -> int:
        if not self.has_discount or not self.price:
            return 0
        # Làm tròn xuống để không hiển thị mức giảm cao hơn thực tế
        return int((self.price - self.sale_price) * 100 // self.price)

    # ---- Tồn kho ----
    @property
    def stock_quantity(self) -> int:
        return self.batches.aggregate(total=Sum("quantity_remaining"))["total"] or 0

    @property
    def in_stock(self) -> bool:
        return self.stock_quantity > 0

    # ---- Đánh giá ----
    @property
    def rating_average(self) -> float:
        return round(self.reviews.aggregate(avg=Avg("rating"))["avg"] or 0, 1)

    @property
    def rating_count(self) -> int:
        return self.reviews.count()

    @property
    def spec_lines(self):
        """Tách thông số kỹ thuật thành danh sách (tên, giá trị)."""
        lines = []
        for raw in (self.specifications or "").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            key, sep, value = raw.partition(":")
            lines.append((key.strip(), value.strip()) if sep else ("", raw))
        return lines


class ProductImage(models.Model):
    """Ảnh phụ của sản phẩm."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Sản phẩm")
    image = models.ImageField("Ảnh", upload_to="products/")
    alt_text = models.CharField("Mô tả ảnh", max_length=200, blank=True)
    display_order = models.PositiveIntegerField("Thứ tự", default=0)

    class Meta:
        verbose_name = "Ảnh sản phẩm"
        verbose_name_plural = "Ảnh sản phẩm"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"Ảnh của {self.product.name}"


class Review(models.Model):
    """Đánh giá sản phẩm của khách hàng."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Sản phẩm")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", verbose_name="Người đánh giá")
    rating = models.PositiveSmallIntegerField(
        "Số sao", validators=[MinValueValidator(1), MaxValueValidator(5)], default=5
    )
    title = models.CharField("Tiêu đề", max_length=200, blank=True)
    content = models.TextField("Nội dung")
    is_approved = models.BooleanField("Đã duyệt", default=True)
    created_at = models.DateTimeField("Ngày đánh giá", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["product", "user"], name="unique_review_per_user_product"),
        ]

    def __str__(self):
        return f"{self.user} đánh giá {self.product} ({self.rating}★)"

    @property
    def star_range(self):
        return range(self.rating)

    @property
    def empty_star_range(self):
        return range(5 - self.rating)
