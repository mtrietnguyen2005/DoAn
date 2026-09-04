"""Cấu hình dành riêng cho kiểm thử.

Mặc định unit test chạy trên SQLite trong bộ nhớ:

* Nhanh hơn nhiều lần so với SQL Server
* Không phụ thuộc vào ``.env`` hay cấu hình máy, nên ai clone dự án về cũng
  chạy được ngay mà không cần cài SQL Server
* Không đụng tới database thật của bạn

Muốn chạy chính bộ test đó trên SQL Server để kiểm tra tương thích
(khuyến nghị làm ít nhất một lần trước khi nộp), đặt biến môi trường
``TEST_ON_MSSQL=True``. Khi đó tài khoản CSDL phải có quyền tạo database
vì Django cần tạo database tạm ``test_PCPartsDB``.
"""
from decouple import config

from .settings import *  # noqa: F401,F403

TEST_ON_MSSQL = config("TEST_ON_MSSQL", default=False, cast=bool)

if not TEST_ON_MSSQL:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

# Không gọi ra Cloudinary khi chạy test
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Gửi email vào bộ nhớ để test kiểm tra được nội dung
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Tắt bớt log cho đầu ra test gọn gàng
LOGGING["root"]["level"] = "WARNING"  # noqa: F405
