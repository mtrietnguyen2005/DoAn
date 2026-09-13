from django.contrib import admin, messages
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from apps.core.admin_mixins import ReadOnlyForStaffMixin

from .models import Batch, StockTransaction
from .services import receive_batch


@admin.register(Batch)
class BatchAdmin(ModelAdmin):
    list_display = (
        "batch_code", "product", "supplier", "quantity_in", "quantity_remaining",
        "cost_price_display", "received_date",
    )
    list_filter = ("supplier", "received_date", "product__category")
    search_fields = ("batch_code", "product__name", "product__sku", "note")
    autocomplete_fields = ("product", "supplier")
    date_hierarchy = "received_date"
    readonly_fields = ("created_at",)
    list_per_page = 25

    def save_model(self, request, obj, form, change):
        creating = obj.pk is None
        if creating and not obj.quantity_remaining:
            obj.quantity_remaining = obj.quantity_in
        super().save_model(request, obj, form, change)
        if creating:
            receive_batch(obj, user=request.user, note=f"Nhập lô {obj.batch_code}")
            messages.success(request, f"Đã ghi nhận giao dịch nhập kho cho lô {obj.batch_code}.")

    @admin.display(description="Giá vốn", ordering="cost_price")
    def cost_price_display(self, obj):
        return f"{obj.cost_price:,.0f}đ"


@admin.register(StockTransaction)
class StockTransactionAdmin(ReadOnlyForStaffMixin, ModelAdmin):

    list_display = ("created_at", "transaction_type", "product", "batch", "quantity_display", "quantity_after", "reference", "created_by")
    list_filter = ("transaction_type", "created_at", "product__category")
    search_fields = ("product__name", "batch__batch_code", "reference", "note")
    autocomplete_fields = ("product", "batch", "created_by")
    date_hierarchy = "created_at"
    list_per_page = 30

    @admin.display(description="Số lượng", ordering="quantity")
    def quantity_display(self, obj):
        color = "#16a34a" if obj.quantity > 0 else "#dc2626"
        return format_html('<strong style="color:{}">{}</strong>', color, f"{obj.quantity:+d}")
