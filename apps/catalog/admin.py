from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from apps.core.admin_mixins import ReadOnlyForStaffMixin

from .models import Brand, Category, Product, ProductImage, Review, Supplier


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "parent", "display_order", "product_count", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("display_order", "is_active")

    @admin.display(description="Số sản phẩm")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("name", "country", "product_count", "is_active")
    list_filter = ("is_active", "country")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Số sản phẩm")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ("name", "contact_person", "phone", "email", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_person", "phone", "email", "tax_code")
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "display_order")


class BatchInline(TabularInline):
    from apps.inventory.models import Batch

    model = Batch
    extra = 0
    fields = ("batch_code", "supplier", "quantity_in", "quantity_remaining", "cost_price", "received_date")
    readonly_fields = ("quantity_remaining",)
    show_change_link = True


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("sku", "name", "category", "brand", "price_display", "stock_display", "rating_display", "is_active", "is_featured")
    list_filter = ("is_active", "is_featured", "category", "brand", "supplier")
    search_fields = ("name", "sku", "description", "short_description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "brand", "supplier")
    list_editable = ("is_active", "is_featured")
    readonly_fields = ("view_count", "created_at", "updated_at", "stock_display")
    inlines = [ProductImageInline, BatchInline]
    list_per_page = 25
    fieldsets = (
        ("Thông tin cơ bản", {"fields": ("name", "slug", "sku", "category", "brand", "supplier", "thumbnail")}),
        ("Mô tả", {"fields": ("short_description", "description", "specifications")}),
        ("Giá & bảo hành", {"fields": ("price", "sale_price", "warranty_months", "weight_gram")}),
        ("Trạng thái", {"fields": ("is_active", "is_featured", "stock_display", "view_count", "created_at", "updated_at")}),
    )

    ordering = ("-created_at", "-id")

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .annotate(stock_total=Sum("batches__quantity_remaining"))
            .order_by(*self.ordering)
        )

    @admin.display(description="Giá bán", ordering="price")
    def price_display(self, obj):
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration:line-through;color:#94a3b8">{}đ</span> '
                '<strong style="color:#dc2626">{}đ</strong>',
                f"{obj.price:,.0f}", f"{obj.sale_price:,.0f}",
            )
        return format_html("<strong>{}đ</strong>", f"{obj.price:,.0f}")

    @admin.display(description="Tồn kho", ordering="stock_total")
    def stock_display(self, obj):
        stock = getattr(obj, "stock_total", None)
        if stock is None:
            stock = obj.stock_quantity
        stock = stock or 0
        color = "#16a34a" if stock > 10 else ("#f59e0b" if stock > 0 else "#dc2626")
        return format_html('<strong style="color:{}">{}</strong>', color, stock)

    @admin.display(description="Đánh giá")
    def rating_display(self, obj):
        return f"{obj.rating_average}★ ({obj.rating_count})" if obj.rating_count else "—"


@admin.register(Review)
class ReviewAdmin(ReadOnlyForStaffMixin, ModelAdmin):

    list_display = ("product", "user", "rating", "title", "is_approved", "created_at")
    list_filter = ("rating", "is_approved", "created_at")
    search_fields = ("product__name", "user__username", "title", "content")
    autocomplete_fields = ("product", "user")
    date_hierarchy = "created_at"
