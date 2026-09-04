from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Người dùng hệ thống (khách hàng và quản trị viên)."""

    class Gender(models.TextChoices):
        MALE = "male", "Nam"
        FEMALE = "female", "Nữ"
        OTHER = "other", "Khác"

    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Số điện thoại", max_length=20, blank=True)
    avatar = models.ImageField("Ảnh đại diện", upload_to="avatars/", blank=True, null=True)
    date_of_birth = models.DateField("Ngày sinh", blank=True, null=True)
    gender = models.CharField("Giới tính", max_length=10, choices=Gender.choices, blank=True)
    created_at = models.DateTimeField("Ngày tạo", default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        ordering = ["-created_at"]

    def __str__(self):
        return self.display_name

    def get_full_name(self):
        """Họ tên theo thứ tự tiếng Việt: Họ đứng trước, Tên đứng sau.

        Ghi đè hàm của Django (vốn ghép first_name + last_name theo kiểu
        phương Tây) vì biểu mẫu của hệ thống đặt last_name = "Họ",
        first_name = "Tên".
        """
        return f"{self.last_name} {self.first_name}".strip()

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None

    @property
    def default_address(self):
        return self.addresses.filter(is_default=True).first() or self.addresses.first()


class Address(models.Model):
    """Địa chỉ nhận hàng của khách hàng."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name="Người dùng")
    full_name = models.CharField("Họ tên người nhận", max_length=120)
    phone = models.CharField("Số điện thoại", max_length=20)
    province = models.CharField("Tỉnh/Thành phố", max_length=100)
    district = models.CharField("Quận/Huyện", max_length=100)
    ward = models.CharField("Phường/Xã", max_length=100)
    street = models.CharField("Địa chỉ cụ thể", max_length=255)
    note = models.CharField("Ghi chú", max_length=255, blank=True)
    is_default = models.BooleanField("Địa chỉ mặc định", default=False)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    class Meta:
        verbose_name = "Địa chỉ nhận hàng"
        verbose_name_plural = "Địa chỉ nhận hàng"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.full_address}"

    @property
    def full_address(self):
        return f"{self.street}, {self.ward}, {self.district}, {self.province}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(pk=self.pk).update(is_default=False)
        elif not Address.objects.filter(user=self.user, is_default=True).exists():
            # Địa chỉ đầu tiên của một người dùng luôn là địa chỉ mặc định.
            # Gán lại cho cả instance đang giữ để nó không lệch với database.
            self.is_default = True
            Address.objects.filter(pk=self.pk).update(is_default=True)
