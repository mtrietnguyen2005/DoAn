"""Nghiệp vụ kho: phân bổ tồn kho theo lô (FIFO) và hoàn trả về đúng lô ban đầu."""
from django.db import transaction

from .models import Batch, StockTransaction


class OutOfStockError(Exception):
    """Không đủ tồn kho để xuất hàng."""


@transaction.atomic
def allocate_stock(product, quantity, *, reference="", user=None, note=""):
    """Trừ tồn kho của ``product`` theo nguyên tắc FIFO (lô nhập kho trước xuất trước).

    Trả về danh sách ``[(batch, số_lượng_lấy, giá_vốn), ...]`` để lưu vào chi tiết đơn hàng.
    Ném ``OutOfStockError`` nếu tồn kho không đủ.

    Hai lô cùng ngày nhập được xếp theo ``id`` để thứ tự xuất kho luôn xác định,
    không phụ thuộc cách cơ sở dữ liệu trả về hàng.
    """
    if quantity <= 0:
        raise ValueError("Số lượng xuất kho phải lớn hơn 0.")

    batches = (
        Batch.objects.select_for_update()
        .filter(product=product, quantity_remaining__gt=0)
        .order_by("received_date", "id")
    )

    available = sum(b.quantity_remaining for b in batches)
    if available < quantity:
        raise OutOfStockError(
            f"Sản phẩm '{product.name}' chỉ còn {available} sản phẩm, không đủ {quantity}."
        )

    allocations, remaining = [], quantity
    for batch in batches:
        if remaining <= 0:
            break
        take = min(batch.quantity_remaining, remaining)
        batch.quantity_remaining -= take
        batch.save(update_fields=["quantity_remaining"])
        StockTransaction.objects.create(
            batch=batch,
            product=product,
            transaction_type=StockTransaction.Type.OUT,
            quantity=-take,
            quantity_after=batch.quantity_remaining,
            reference=reference,
            note=note or "Xuất kho bán hàng",
            created_by=user,
        )
        allocations.append((batch, take, batch.cost_price))
        remaining -= take

    return allocations


@transaction.atomic
def return_stock(batch, quantity, *, reference="", user=None, note=""):
    """Hoàn trả ``quantity`` sản phẩm về đúng ``batch`` ban đầu."""
    if quantity <= 0:
        return
    locked = Batch.objects.select_for_update().get(pk=batch.pk)
    locked.quantity_remaining += quantity
    if locked.quantity_remaining > locked.quantity_in:
        locked.quantity_in = locked.quantity_remaining
        locked.save(update_fields=["quantity_remaining", "quantity_in"])
    else:
        locked.save(update_fields=["quantity_remaining"])
    StockTransaction.objects.create(
        batch=locked,
        product=locked.product,
        transaction_type=StockTransaction.Type.RETURN,
        quantity=quantity,
        quantity_after=locked.quantity_remaining,
        reference=reference,
        note=note or "Hoàn kho do hủy đơn hàng",
        created_by=user,
    )


@transaction.atomic
def receive_batch(batch, *, user=None, note=""):
    """Ghi nhận giao dịch nhập kho cho một lô hàng mới tạo."""
    locked = Batch.objects.select_for_update().get(pk=batch.pk)
    StockTransaction.objects.create(
        batch=locked,
        product=locked.product,
        transaction_type=StockTransaction.Type.IN,
        quantity=locked.quantity_in,
        quantity_after=locked.quantity_remaining,
        reference=locked.batch_code,
        note=note or "Nhập kho lô hàng mới",
        created_by=user,
    )


@transaction.atomic
def adjust_batch(batch, new_quantity, *, user=None, note=""):
    """Điều chỉnh thủ công tồn kho của một lô và ghi vết giao dịch."""
    locked = Batch.objects.select_for_update().get(pk=batch.pk)
    delta = new_quantity - locked.quantity_remaining
    if delta == 0:
        return
    locked.quantity_remaining = new_quantity
    if locked.quantity_remaining > locked.quantity_in:
        locked.quantity_in = locked.quantity_remaining
    locked.save(update_fields=["quantity_remaining", "quantity_in"])
    StockTransaction.objects.create(
        batch=locked,
        product=locked.product,
        transaction_type=StockTransaction.Type.ADJUST,
        quantity=delta,
        quantity_after=locked.quantity_remaining,
        reference=locked.batch_code,
        note=note or "Điều chỉnh tồn kho thủ công",
        created_by=user,
    )
