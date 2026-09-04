from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def merge_session_cart(sender, request, user, **kwargs):
    """Đồng bộ giỏ hàng lưu trong session vào giỏ hàng của tài khoản khi đăng nhập."""
    from apps.orders.cart import Cart

    Cart(request).merge_into_user(user)
