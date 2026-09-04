from django.db import models
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Product, unique_slug


class Banner(models.Model):
    """Banner quảng cáo hiển thị trên trang chủ."""

    class Position(models.TextChoices):
        HERO = "hero", "Slider trang chủ"
        SIDEBAR = "sidebar", "Cột bên"
        FOOTER = "footer", "Chân trang"

    title = models.CharField("Tiêu đề", max_length=200)
    subtitle = models.CharField("Mô tả ngắn", max_length=300, blank=True)
    image = models.ImageField("Ảnh banner", upload_to="banners/")
    link = models.CharField("Đường dẫn khi bấm vào", max_length=500, blank=True)
    button_text = models.CharField("Chữ trên nút", max_length=60, blank=True, default="Xem ngay")
    position = models.CharField("Vị trí", max_length=20, choices=Position.choices, default=Position.HERO)
    display_order = models.PositiveIntegerField("Thứ tự", default=0)
    start_date = models.DateTimeField("Bắt đầu hiển thị", default=timezone.now)
    end_date = models.DateTimeField("Kết thúc hiển thị", null=True, blank=True)
    is_active = models.BooleanField("Đang hiển thị", default=True)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banner"
        ordering = ["display_order", "-id"]

    def __str__(self):
        return self.title

    @property
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now and (self.end_date is None or now <= self.end_date)


class News(models.Model):
    """Tin tức, bài viết công nghệ."""

    title = models.CharField("Tiêu đề", max_length=255)
    slug = models.SlugField("Đường dẫn", max_length=280, unique=True, blank=True)
    thumbnail = models.ImageField("Ảnh đại diện", upload_to="news/", blank=True, null=True)
    summary = models.CharField("Tóm tắt", max_length=400, blank=True)
    content = models.TextField("Nội dung")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="news_posts", verbose_name="Tác giả",
    )
    tags = models.CharField("Thẻ (phân cách bằng dấu phẩy)", max_length=255, blank=True)
    is_published = models.BooleanField("Đã xuất bản", default=True)
    published_at = models.DateTimeField("Ngày xuất bản", default=timezone.now)
    view_count = models.PositiveIntegerField("Lượt xem", default=0)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Tin tức"
        verbose_name_plural = "Tin tức"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("content:news_detail", kwargs={"slug": self.slug})

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class Promotion(models.Model):
    """Chương trình khuyến mãi."""

    title = models.CharField("Tên chương trình", max_length=255)
    slug = models.SlugField("Đường dẫn", max_length=280, unique=True, blank=True)
    banner = models.ImageField("Ảnh chương trình", upload_to="promotions/", blank=True, null=True)
    description = models.TextField("Mô tả", blank=True)
    discount_percent = models.PositiveSmallIntegerField("Giảm giá (%)", default=0)
    products = models.ManyToManyField(
        Product, blank=True, related_name="promotions", verbose_name="Sản phẩm áp dụng"
    )
    start_date = models.DateTimeField("Bắt đầu", default=timezone.now)
    end_date = models.DateTimeField("Kết thúc")
    is_active = models.BooleanField("Đang chạy", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("content:promotion_detail", kwargs={"slug": self.slug})

    @property
    def is_running(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def days_left(self):
        return max((self.end_date - timezone.now()).days, 0)
