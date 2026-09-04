from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import Banner, News, Promotion


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ("preview", "title", "position", "display_order", "start_date", "end_date", "is_active")
    list_filter = ("position", "is_active")
    search_fields = ("title", "subtitle")
    list_editable = ("display_order", "is_active")

    @admin.display(description="Ảnh")
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px" />', obj.image.url)
        return "—"


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ("title", "author", "published_at", "view_count", "is_published")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "summary", "content", "tags")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author",)
    date_hierarchy = "published_at"
    readonly_fields = ("view_count", "created_at")
    list_editable = ("is_published",)

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Promotion)
class PromotionAdmin(ModelAdmin):
    list_display = ("title", "discount_percent", "start_date", "end_date", "product_count", "is_active")
    list_filter = ("is_active", "start_date")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("products",)
    list_editable = ("is_active",)

    @admin.display(description="Số sản phẩm")
    def product_count(self, obj):
        return obj.products.count()
