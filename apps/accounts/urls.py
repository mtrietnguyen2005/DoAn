from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-xuat/", views.logout_view, name="logout"),
    path("ho-so/", views.profile_view, name="profile"),
    path("doi-mat-khau/", views.password_change_view, name="password_change"),
    path("dia-chi/", views.address_list, name="address_list"),
    path("dia-chi/them/", views.address_create, name="address_create"),
    path("dia-chi/<int:pk>/sua/", views.address_update, name="address_update"),
    path("dia-chi/<int:pk>/xoa/", views.address_delete, name="address_delete"),
    path("dia-chi/<int:pk>/mac-dinh/", views.address_set_default, name="address_set_default"),
    path("danh-gia-cua-toi/", views.my_reviews, name="my_reviews"),
]
