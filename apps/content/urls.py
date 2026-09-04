from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path("", views.news_list, name="news_list"),
    path("khuyen-mai/", views.promotion_list, name="promotion_list"),
    path("khuyen-mai/<slug:slug>/", views.promotion_detail, name="promotion_detail"),
    path("<slug:slug>/", views.news_detail, name="news_detail"),
]
