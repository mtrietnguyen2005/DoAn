from django.contrib import admin, messages
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Order, OrderItem, OrderItemBatch, OrderStatusHistory, PromoCode, Shipping,
)
from .services import OrderError, change_order_status


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "product_name", "product_sku", "unit_price", "cost_price", "quantity", "line_total_display", "line_profit_display")
    readonly_fields = ("line_total_display", "line_profit_display")
    autocomplete_fields = ("product",)

    @admin.display(description="Thành tiền")
    def line_total_display(self, obj):
        return f"{obj.line_total:,.0f}đ" if obj.pk else "—"

    @admin.display(description="Lợi nhuận")
    def line_profit_display(self, obj):
        return f"{obj.line_profit:,.0f}đ" if obj.pk else "—"


class OrderStatusHistoryInline(TabularInline):
    model = OrderStatusHistory
    extra = 0
    fields = ("created_at", "from_status", "to_status", "note", "changed_by")
    readonly_fields = ("created_at", "from_status", "to_status", "note", "changed_by")
    can_delete = False
    ordering = ("created_at",)

    def has_add_permission(self, request, obj=None):
        return False


class OrderItemBatchInline(TabularInline):
    model = OrderItemBatch
    extra = 0
    fields = ("batch", "quantity", "cost_price", "is_returned")
    readonly_fields = ("batch", "quantity", "cost_price", "is_returned")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("code", "receiver_name", "receiver_phone", "total_display", "profit_display", "status_badge", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("code", "receiver_name", "receiver_phone", "receiver_email", "user__username")
    autocomplete_fields = ("user", "promo_code")
    date_hierarchy = "created_at"
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = ("code", "subtotal", "total", "created_at", "updated_at", "completed_at", "cancelled_at", "profit_display")
    list_per_page = 25
    actions = ["mark_confirmed", "mark_shipping", "mark_completed", "mark_cancelled"]
    fieldsets = (
        ("Đơn hàng", {"fields": ("code", "user", "status", "payment_method", "created_at", "updated_at")}),
        ("Người nhận", {"fields": ("receiver_name", "receiver_phone", "receiver_email", "shipping_address")}),
        ("Thanh toán", {"fields": ("subtotal", "shipping_fee", "promo_code", "discount_amount", "total", "profit_display")}),
        ("Ghi chú", {"fields": ("customer_note", "admin_note")}),
        ("Mốc thời gian", {"fields": ("completed_at", "cancelled_at")}),
    )

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data:
            new_status = obj.status
            obj.status = form.initial.get("status", obj.status)
            super().save_model(request, obj, form, change)
            try:
                change_order_status(obj, new_status, user=request.user, note="Quản trị viên cập nhật trạng thái")
            except OrderError as exc:
                messages.error(request, str(exc))
            else:
                messages.success(request, f"Đơn {obj.code} đã chuyển sang: {obj.get_status_display()}")
            return
        super().save_model(request, obj, form, change)

    def _bulk_change(self, request, queryset, status, label):
        ok = failed = 0
        for order in queryset:
            try:
                change_order_status(order, status, user=request.user, note=f"Thao tác hàng loạt: {label}")
                ok += 1
            except OrderError:
                failed += 1
        messages.success(request, f"Đã cập nhật {ok} đơn hàng sang '{label}'.")
        if failed:
            messages.warning(request, f"{failed} đơn không thể chuyển trạng thái.")

    @admin.action(description="Xác nhận đơn hàng đã chọn")
    def mark_confirmed(self, request, queryset):
        self._bulk_change(request, queryset, Order.Status.CONFIRMED, "Đã xác nhận")

    @admin.action(description="Chuyển sang Đang giao")
    def mark_shipping(self, request, queryset):
        self._bulk_change(request, queryset, Order.Status.SHIPPING, "Đang giao")

    @admin.action(description="Hoàn thành đơn hàng")
    def mark_completed(self, request, queryset):
        self._bulk_change(request, queryset, Order.Status.COMPLETED, "Hoàn thành")

    @admin.action(description="Hủy đơn hàng (tự động hoàn kho)")
    def mark_cancelled(self, request, queryset):
        self._bulk_change(request, queryset, Order.Status.CANCELLED, "Đã hủy")

    @admin.display(description="Tổng tiền", ordering="total")
    def total_display(self, obj):
        return format_html("<strong>{}đ</strong>", f"{obj.total:,.0f}")

    @admin.display(description="Lợi nhuận")
    def profit_display(self, obj):
        if not obj.pk:
            return "—"
        profit = obj.profit
        color = "#16a34a" if profit >= 0 else "#dc2626"
        return format_html('<strong style="color:{}">{}đ</strong>', color, f"{profit:,.0f}")

    @admin.display(description="Trạng thái", ordering="status")
    def status_badge(self, obj):
        colors = {
            Order.Status.PENDING: ("#fef3c7", "#92400e"),
            Order.Status.CONFIRMED: ("#dbeafe", "#1e40af"),
            Order.Status.SHIPPING: ("#e0e7ff", "#3730a3"),
            Order.Status.COMPLETED: ("#d1fae5", "#065f46"),
            Order.Status.CANCELLED: ("#fee2e2", "#991b1b"),
        }
        bg, fg = colors.get(obj.status, ("#f1f5f9", "#334155"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:999px;font-weight:600;font-size:12px">{}</span>',
            bg, fg, obj.get_status_display(),
        )


@admin.register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("order", "product_name", "unit_price", "cost_price", "quantity", "line_total_display", "line_profit_display")
    list_filter = ("order__status",)
    search_fields = ("order__code", "product_name", "product_sku")
    autocomplete_fields = ("order", "product")
    inlines = [OrderItemBatchInline]

    @admin.display(description="Thành tiền")
    def line_total_display(self, obj):
        return f"{obj.line_total:,.0f}đ"

    @admin.display(description="Lợi nhuận")
    def line_profit_display(self, obj):
        return f"{obj.line_profit:,.0f}đ"


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(ModelAdmin):
    list_display = ("order", "from_status", "to_status", "note", "changed_by", "created_at")
    list_filter = ("to_status", "created_at")
    search_fields = ("order__code", "note")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Shipping)
class ShippingAdmin(ModelAdmin):
    list_display = ("order", "carrier", "tracking_code", "fee", "estimated_date", "shipped_at", "delivered_at")
    list_filter = ("carrier", "estimated_date")
    search_fields = ("order__code", "tracking_code")
    autocomplete_fields = ("order",)


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = ("code", "discount_type", "value", "min_order_value", "usage_display", "start_date", "end_date", "is_active")
    list_filter = ("discount_type", "is_active", "start_date")
    search_fields = ("code", "description")
    readonly_fields = ("used_count", "created_at")
    list_editable = ("is_active",)

    @admin.display(description="Lượt dùng")
    def usage_display(self, obj):
        limit = obj.usage_limit or "∞"
        return f"{obj.used_count}/{limit}"
