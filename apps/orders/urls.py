from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("them/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cap-nhat/<int:product_id>/", views.cart_update, name="cart_update"),
    path("xoa/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("xoa-tat-ca/", views.cart_clear, name="cart_clear"),
    path("dong-bo/", views.cart_sync, name="cart_sync"),
    path("so-luong/", views.cart_count, name="cart_count"),
    path("ma-giam-gia/ap-dung/", views.promo_apply, name="promo_apply"),
    path("ma-giam-gia/go/", views.promo_remove, name="promo_remove"),
    path("thanh-toan/", views.checkout, name="checkout"),
    path("dat-hang-thanh-cong/<str:code>/", views.order_success, name="order_success"),
    path("don-hang/", views.order_list, name="order_list"),
    path("don-hang/<str:code>/", views.order_detail, name="order_detail"),
    path("don-hang/<str:code>/huy/", views.order_cancel, name="order_cancel"),
]
