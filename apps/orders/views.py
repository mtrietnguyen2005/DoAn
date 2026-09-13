import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .cart import Cart
from .forms import CancelOrderForm, CheckoutForm
from .models import Order, PromoCode
from .services import OrderError, calculate_shipping_fee, cancel_order, create_order

PROMO_SESSION_KEY = "promo_code"


def _cart_response(request, cart, message="", ok=True):
    if request.headers.get("HX-Request"):
        response = render(request, "orders/partials/cart_summary.html", {"cart": cart, "items": cart.get_items()})
        response["HX-Trigger"] = json.dumps({"cartUpdated": {"count": len(cart), "message": message, "ok": ok}})
        return response
    return JsonResponse({
        "ok": ok,
        "message": message,
        "count": len(cart),
        "subtotal": float(cart.subtotal),
    })


def cart_detail(request):
    cart = Cart(request)
    items = cart.get_items()
    subtotal = sum((i["line_total"] for i in items), 0)
    promo, discount = _get_session_promo(request, subtotal)
    shipping_fee = calculate_shipping_fee(subtotal) if items else 0
    context = {
        "cart": cart,
        "items": items,
        "subtotal": subtotal,
        "promo": promo,
        "discount": discount,
        "shipping_fee": shipping_fee,
        "total": subtotal + shipping_fee - discount,
    }
    return render(request, "orders/cart_detail.html", context)


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product.objects.active(), pk=product_id)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    if product.stock_quantity <= 0:
        return _cart_response(request, cart, "Sản phẩm đã hết hàng.", ok=False)
    added = cart.add(product, quantity)
    message = f"Đã thêm '{product.name}' vào giỏ hàng." if added else "Không thể thêm sản phẩm."
    if request.headers.get("HX-Request") or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _cart_response(request, cart, message, ok=bool(added))
    messages.success(request, message)
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product.objects.active(), pk=product_id)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    cart.add(product, quantity, replace=True)
    if request.headers.get("HX-Request") or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _cart_response(request, cart, "Đã cập nhật giỏ hàng.")
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart = Cart(request)
    cart.remove(product)
    if request.headers.get("HX-Request") or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return _cart_response(request, cart, f"Đã xóa '{product.name}' khỏi giỏ hàng.")
    messages.success(request, f"Đã xóa '{product.name}' khỏi giỏ hàng.")
    return redirect("orders:cart_detail")


@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    request.session.pop(PROMO_SESSION_KEY, None)
    if request.headers.get("HX-Request"):
        return _cart_response(request, cart, "Đã xóa toàn bộ giỏ hàng.")
    messages.success(request, "Đã xóa toàn bộ giỏ hàng.")
    return redirect("orders:cart_detail")


@require_POST
def cart_sync(request):
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        payload = {}
    cart = Cart(request)
    cart.set_from_payload(payload.get("items", {}))
    return JsonResponse({"ok": True, "count": len(cart)})


def cart_count(request):
    return JsonResponse({"count": len(Cart(request))})


def _get_session_promo(request, subtotal):
    code = request.session.get(PROMO_SESSION_KEY)
    if not code:
        return None, 0
    promo = PromoCode.objects.filter(code=code).first()
    if not promo or promo.error_for(subtotal):
        request.session.pop(PROMO_SESSION_KEY, None)
        return None, 0
    return promo, promo.calculate_discount(subtotal)


@require_POST
def promo_apply(request):
    code = request.POST.get("code", "").strip().upper()
    cart = Cart(request)
    subtotal = cart.subtotal
    promo = PromoCode.objects.filter(code=code).first()
    if not promo:
        messages.error(request, "Mã giảm giá không tồn tại.")
    else:
        error = promo.error_for(subtotal)
        if error:
            messages.error(request, error)
        else:
            request.session[PROMO_SESSION_KEY] = promo.code
            messages.success(request, f"Đã áp dụng mã {promo.code}: giảm {promo.calculate_discount(subtotal):,.0f}đ.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def promo_remove(request):
    request.session.pop(PROMO_SESSION_KEY, None)
    messages.info(request, "Đã gỡ mã giảm giá.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    items = cart.get_items()
    if not items:
        messages.warning(request, "Giỏ hàng đang trống, hãy chọn sản phẩm trước khi đặt hàng.")
        return redirect("catalog:product_list")

    subtotal = sum((i["line_total"] for i in items), 0)
    promo, discount = _get_session_promo(request, subtotal)
    shipping_fee = calculate_shipping_fee(subtotal)

    initial = {}
    address = request.user.default_address
    if address:
        initial = {
            "receiver_name": address.full_name,
            "receiver_phone": address.phone,
            "province": address.province,
            "district": address.district,
            "ward": address.ward,
            "street": address.street,
        }
    initial.setdefault("receiver_name", request.user.display_name)
    initial.setdefault("receiver_phone", request.user.phone)
    initial.setdefault("receiver_email", request.user.email)

    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            order = create_order(
                user=request.user,
                cart=cart,
                receiver_name=form.cleaned_data["receiver_name"],
                receiver_phone=form.cleaned_data["receiver_phone"],
                receiver_email=form.cleaned_data["receiver_email"],
                shipping_address=form.full_address,
                customer_note=form.cleaned_data["customer_note"],
                promo=promo,
                payment_method=form.cleaned_data["payment_method"],
            )
        except OrderError as exc:
            messages.error(request, str(exc))
        else:
            request.session.pop(PROMO_SESSION_KEY, None)
            messages.success(request, f"Đặt hàng thành công! Mã đơn hàng của bạn là {order.code}.")
            return redirect("orders:order_success", code=order.code)

    context = {
        "form": form,
        "items": items,
        "subtotal": subtotal,
        "promo": promo,
        "discount": discount,
        "shipping_fee": shipping_fee,
        "total": subtotal + shipping_fee - discount,
        "addresses": request.user.addresses.all(),
    }
    return render(request, "orders/checkout.html", context)


@login_required
def order_success(request, code):
    order = get_object_or_404(Order.objects.prefetch_related("items"), code=code, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    status = request.GET.get("status", "")
    if status:
        orders = orders.filter(status=status)
    page = Paginator(orders, 10).get_page(request.GET.get("page"))
    context = {
        "page_obj": page,
        "orders": page.object_list,
        "status_choices": Order.Status.choices,
        "current_status": status,
    }
    return render(request, "orders/order_list.html", context)


@login_required
def order_detail(request, code):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product", "status_history").select_related("shipping"),
        code=code, user=request.user,
    )
    return render(request, "orders/order_detail.html", {"order": order, "cancel_form": CancelOrderForm()})


@login_required
@require_POST
def order_cancel(request, code):
    order = get_object_or_404(Order, code=code, user=request.user)
    form = CancelOrderForm(request.POST)
    reason = form.cleaned_data["reason"] if form.is_valid() else ""
    try:
        cancel_order(order, user=request.user, reason=f"Khách hàng hủy đơn. {reason}".strip())
    except OrderError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, f"Đã hủy đơn hàng {order.code}. Số lượng sản phẩm đã được hoàn về kho.")
    return redirect("orders:order_detail", code=order.code)
