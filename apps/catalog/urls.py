from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("san-pham/", views.product_list, name="product_list"),
    path("thuong-hieu/", views.brand_list, name="brand_list"),
    path("nha-cung-cap/", views.supplier_list, name="supplier_list"),
    path("nha-cung-cap/<slug:slug>/", views.supplier_detail, name="supplier_detail"),
    path("danh-gia/<int:pk>/sua/", views.review_update, name="review_update"),
    path("danh-gia/<int:pk>/xoa/", views.review_delete, name="review_delete"),
    path("san-pham/<slug:slug>/", views.product_detail, name="product_detail"),
    path("san-pham/<slug:slug>/danh-gia/", views.review_create, name="review_create"),
]
