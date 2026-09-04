from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_mixins import ReadOnlyForStaffMixin

from .models import Address, User


class AddressInline(TabularInline):
    model = Address
    extra = 0
    fields = ("full_name", "phone", "province", "district", "ward", "street", "is_default")

    def has_add_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_superuser)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ("username", "email", "full_name", "phone", "is_staff", "is_active", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active", "gender")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    ordering = ("-created_at",)
    inlines = [AddressInline]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Thông tin cá nhân", {
            "fields": ("last_name", "first_name", "email", "phone", "avatar", "date_of_birth", "gender")
        }),
        ("Phân quyền", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Mốc thời gian", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    @admin.display(description="Họ tên")
    def full_name(self, obj):
        return obj.get_full_name() or "—"


@admin.register(Address)
class AddressAdmin(ReadOnlyForStaffMixin, ModelAdmin):
    """Chỉ đọc với Admin thường (theo yêu cầu phân quyền)."""

    list_display = ("full_name", "user", "phone", "province", "district", "is_default", "created_at")
    list_filter = ("is_default", "province")
    search_fields = ("full_name", "phone", "user__username", "street")
    autocomplete_fields = ("user",)
