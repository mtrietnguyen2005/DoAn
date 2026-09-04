"""Nghiệp vụ đơn hàng: đặt hàng, đổi trạng thái, hoàn kho khi hủy."""
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.inventory.services import OutOfStockError, allocate_stock, return_stock

from .models import Order, OrderItem, OrderItemBatch, OrderStatusHistory, Shipping


class OrderError(Exception):
    """Lỗi nghiệp vụ đơn hàng."""


def calculate_shipping_fee(subtotal) -> Decimal:
    """Miễn phí vận chuyển khi đơn đạt ngưỡng cấu hình."""
    if subtotal >= settings.FREE_SHIPPING_THRESHOLD:
        return Decimal(0)
    return Decimal(settings.DEFAULT_SHIPPING_FEE)


@transaction.atomic
def create_order(*, user, cart, receiver_name, receiver_phone, receiver_email="",
                 shipping_address, customer_note="", promo=None, payment_method=Order.PaymentMethod.COD):
    """Tạo đơn hàng từ giỏ hàng: trừ kho theo lô, lưu giá vốn, ghi lịch sử trạng thái."""
    items = cart.get_items()
    if not items:
        raise OrderError("Giỏ hàng đang trống.")

    subtotal = sum(item["line_total"] for item in items)
    discount = promo.calculate_discount(subtotal) if promo else Decimal(0)
    shipping_fee = calculate_shipping_fee(subtotal)

    order = Order.objects.create(
        user=user if user and user.is_authenticated else None,
        receiver_name=receiver_name,
        receiver_phone=receiver_phone,
        receiver_email=receiver_email,
        shipping_address=shipping_address,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_amount=discount,
        total=subtotal + shipping_fee - discount,
        promo_code=promo,
        payment_method=payment_method,
        customer_note=customer_note,
        status=Order.Status.PENDING,
    )

    actor = user if user and user.is_authenticated else None

    for item in items:
        product = item["product"]
        quantity = item["quantity"]
        try:
            allocations = allocate_stock(
                product, quantity, reference=order.code or f"Order#{order.pk}",
                user=actor, note=f"Xuất kho cho đơn {order.code}",
            )
        except OutOfStockError as exc:
            raise OrderError(str(exc)) from exc

        total_cost = sum(qty * cost for _, qty, cost in allocations)
        avg_cost = Decimal(int(total_cost / quantity)) if quantity else Decimal(0)

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=item["unit_price"],
            cost_price=avg_cost,
            quantity=quantity,
        )
        OrderItemBatch.objects.bulk_create([
            OrderItemBatch(order_item=order_item, batch=batch, quantity=qty, cost_price=cost)
            for batch, qty, cost in allocations
        ])

    Shipping.objects.create(order=order, fee=shipping_fee)

    OrderStatusHistory.objects.create(
        order=order,
        from_status="",
        to_status=Order.Status.PENDING,
        note="Khách hàng đặt hàng thành công",
        changed_by=actor,
    )

    if promo:
        type(promo).objects.filter(pk=promo.pk).update(used_count=F("used_count") + 1)

    cart.clear()
    return order


@transaction.atomic
def change_order_status(order, new_status, *, user=None, note=""):
    """Đổi trạng thái đơn hàng, ghi lịch sử và hoàn kho khi hủy."""
    if new_status == order.status:
        return order

    valid = dict(Order.Status.choices)
    if new_status not in valid:
        raise OrderError("Trạng thái không hợp lệ.")

    if order.status == Order.Status.CANCELLED:
        raise OrderError("Đơn hàng đã hủy, không thể đổi trạng thái.")
    if order.status == Order.Status.COMPLETED and new_status != Order.Status.CANCELLED:
        raise OrderError("Đơn hàng đã hoàn thành, không thể đổi trạng thái.")

    old_status = order.status
    order.status = new_status

    if new_status == Order.Status.CANCELLED:
        order.cancelled_at = timezone.now()
        if old_status in Order.STOCK_DEDUCTED_STATUSES:
            restore_stock(order, user=user)
        if order.promo_code_id:
            type(order.promo_code).objects.filter(pk=order.promo_code_id, used_count__gt=0).update(
                used_count=F("used_count") - 1
            )
    elif new_status == Order.Status.COMPLETED:
        order.completed_at = timezone.now()
        shipping = getattr(order, "shipping", None)
        if shipping and not shipping.delivered_at:
            shipping.delivered_at = timezone.now()
            shipping.save(update_fields=["delivered_at"])
    elif new_status == Order.Status.SHIPPING:
        shipping = getattr(order, "shipping", None)
        if shipping and not shipping.shipped_at:
            shipping.shipped_at = timezone.now()
            shipping.save(update_fields=["shipped_at"])

    order.save()

    OrderStatusHistory.objects.create(
        order=order,
        from_status=old_status,
        to_status=new_status,
        note=note or f"Chuyển trạng thái sang {valid[new_status]}",
        changed_by=user if user and getattr(user, "is_authenticated", False) else None,
    )
    return order


@transaction.atomic
def restore_stock(order, *, user=None):
    """Hoàn trả toàn bộ số lượng của đơn về đúng lô hàng ban đầu."""
    allocations = (
        OrderItemBatch.objects.select_related("batch", "order_item")
        .filter(order_item__order=order, is_returned=False)
    )
    for allocation in allocations:
        return_stock(
            allocation.batch, allocation.quantity,
            reference=order.code,
            user=user if user and getattr(user, "is_authenticated", False) else None,
            note=f"Hoàn kho do hủy đơn {order.code}",
        )
        allocation.is_returned = True
        allocation.save(update_fields=["is_returned"])


def cancel_order(order, *, user=None, reason=""):
    """Khách hàng hủy đơn (chỉ khi đơn chưa được giao)."""
    if not order.can_cancel:
        raise OrderError("Đơn hàng đang được giao hoặc đã kết thúc, không thể hủy.")
    return change_order_status(
        order, Order.Status.CANCELLED, user=user, note=reason or "Khách hàng hủy đơn hàng"
    )
