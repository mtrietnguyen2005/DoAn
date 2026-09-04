from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "LinhKienPC · Quản trị"
admin.site.site_title = "LinhKienPC Admin"
admin.site.index_title = "Bảng điều khiển"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tai-khoan/", include("apps.accounts.urls")),
    path("gio-hang/", include("apps.orders.urls")),
    path("tin-tuc/", include("apps.content.urls")),
    path("", include("apps.catalog.urls")),
    path("", include("apps.core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
