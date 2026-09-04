"""Dữ liệu cho trang Bảng điều khiển của Admin (django-unfold DASHBOARD_CALLBACK)."""
from datetime import timedelta

from django.conf import settings
from django.db.models import Count, F, Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Product, Review
from apps.inventory.models import Batch
from apps.orders.models import Order, OrderItem


def dashboard_callback(request, context):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    warning_date = today + timedelta(days=settings.EXPIRY_WARNING_DAYS)

    completed = Order.objects.filter(status=Order.Status.COMPLETED)
    revenue_month = completed.filter(created_at__date__gte=month_start).aggregate(s=Sum("total"))["s"] or 0

    cost_month = (
        OrderItem.objects.filter(
            order__status=Order.Status.COMPLETED, order__created_at__date__gte=month_start
        ).aggregate(s=Sum(F("cost_price") * F("quantity")))["s"]
        or 0
    )

    # Lô hàng sắp hết hạn
    expiring_batches = (
        Batch.objects.select_related("product")
        .filter(quantity_remaining__gt=0, expiry_date__isnull=False, expiry_date__lte=warning_date)
        .order_by("expiry_date")[:10]
    )

    # Sản phẩm sắp hết / đã hết tồn kho
    low_stock_products = (
        Product.objects.active()
        .annotate(stock_total=Sum("batches__quantity_remaining"))
        .filter(stock_total__lte=settings.LOW_STOCK_THRESHOLD)
        .order_by("stock_total")[:10]
    )

    status_counts = {
        row["status"]: row["c"]
        for row in Order.objects.values("status").annotate(c=Count("id"))
    }

    context.update({
        "stat_cards": [
            {"title": "Người dùng", "value": User.objects.count(), "icon": "group",
             "sub": f"{User.objects.filter(created_at__date__gte=month_start).count()} mới trong tháng"},
            {"title": "Sản phẩm", "value": Product.objects.count(), "icon": "memory",
             "sub": f"{Product.objects.filter(is_active=True).count()} đang kinh doanh"},
            {"title": "Đơn hàng", "value": Order.objects.count(), "icon": "receipt_long",
             "sub": f"{status_counts.get(Order.Status.PENDING, 0)} chờ xác nhận"},
            {"title": "Đánh giá", "value": Review.objects.count(), "icon": "star",
             "sub": f"{Review.objects.filter(is_approved=False).count()} chờ duyệt"},
        ],
        "revenue_month": revenue_month,
        "profit_month": revenue_month - cost_month,
        "order_status_counts": [
            {"label": label, "value": status_counts.get(value, 0), "code": value}
            for value, label in Order.Status.choices
        ],
        "expiring_batches": expiring_batches,
        "low_stock_products": low_stock_products,
        "recent_orders": Order.objects.select_related("user").order_by("-created_at")[:8],
        "expiry_warning_days": settings.EXPIRY_WARNING_DAYS,
        "low_stock_threshold": settings.LOW_STOCK_THRESHOLD,
    })
    return context
