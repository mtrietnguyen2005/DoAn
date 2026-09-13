from django.conf import settings

from apps.catalog.models import Category
from apps.orders.cart import Cart


def shop_context(request):
    try:
        cart_count = len(Cart(request))
    except Exception:
        cart_count = 0

    return {
        "SHOP_NAME": settings.SHOP_NAME,
        "SHOP_HOTLINE": settings.SHOP_HOTLINE,
        "SHOP_EMAIL": settings.SHOP_EMAIL,
        "SHOP_ADDRESS": settings.SHOP_ADDRESS,
        "nav_categories": Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children"),
        "cart_count": cart_count,
        "FREE_SHIPPING_THRESHOLD": settings.FREE_SHIPPING_THRESHOLD,
    }
