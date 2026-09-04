from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Review
from apps.orders.models import Order

from .forms import AddressForm, LoginForm, ProfileForm, RegisterForm
from .models import Address


def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="apps.accounts.backends.EmailOrUsernameBackend")
        messages.success(request, f"Chào mừng {user.display_name}! Tài khoản đã được tạo thành công.")
        return redirect("core:home")
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if not form.cleaned_data.get("remember_me"):
            request.session.set_expiry(0)  # hết phiên khi đóng trình duyệt
        messages.success(request, f"Xin chào {user.display_name}!")
        return redirect(request.GET.get("next") or "core:home")
    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("core:home")


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật hồ sơ.")
        return redirect("accounts:profile")
    context = {
        "form": form,
        "order_count": Order.objects.filter(user=request.user).count(),
        "review_count": Review.objects.filter(user=request.user).count(),
        "address_count": request.user.addresses.count(),
    }
    return render(request, "accounts/profile.html", context)


@login_required
def password_change_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = (
            "w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm "
            "focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none"
        )
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Đã đổi mật khẩu thành công.")
        return redirect("accounts:profile")
    return render(request, "accounts/password_change.html", {"form": form})


# ---------------------------------------------------------------- Địa chỉ
@login_required
def address_list(request):
    return render(request, "accounts/address_list.html", {"addresses": request.user.addresses.all()})


@login_required
def address_create(request):
    form = AddressForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, "Đã thêm địa chỉ nhận hàng.")
        return redirect("accounts:address_list")
    return render(request, "accounts/address_form.html", {"form": form, "title": "Thêm địa chỉ mới"})


@login_required
def address_update(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    form = AddressForm(request.POST or None, instance=address)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Đã cập nhật địa chỉ.")
        return redirect("accounts:address_list")
    return render(request, "accounts/address_form.html", {"form": form, "title": "Cập nhật địa chỉ"})


@login_required
@require_POST
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Đã xóa địa chỉ.")
    return redirect("accounts:address_list")


@login_required
@require_POST
def address_set_default(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, "Đã đặt làm địa chỉ mặc định.")
    return redirect("accounts:address_list")


# ---------------------------------------------------------------- Đánh giá của tôi
@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related("product").order_by("-created_at")
    return render(request, "accounts/my_reviews.html", {"reviews": reviews})
