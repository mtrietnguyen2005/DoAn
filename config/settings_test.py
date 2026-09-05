"""Cấu hình dành riêng cho kiểm thử.

Mặc định unit test chạy trên SQLite ghi ra tệp ``.pytest-db.sqlite3``:

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
    # CSDL test là một TỆP chứ không phải ``:memory:``.
    #
    # Lý do: test E2E chạy qua ``live_server``, tức một máy chủ WSGI đa
    # luồng. Với SQLite trong bộ nhớ, Django buộc mọi luồng xử lý request
    # phải DÙNG CHUNG một đối tượng connection duy nhất (xem
    # ``LiveServerThread.connections_override`` trong
    # django/test/testcases.py). Hai request đồng thời — chuyện xảy ra
    # thường xuyên khi trang admin vừa tải HTML vừa gọi autocomplete —
    # sẽ khoá nhau vĩnh viễn trên cùng connection đó, và cả lần chạy
    # đứng im chứ không báo lỗi.
    #
    # Với CSDL dạng tệp, mỗi luồng mở connection riêng nên không còn tranh
    # chấp. Đo thực tế: 306 test không-E2E chạy 5,95s (tệp) so với 5,64s
    # (bộ nhớ) — chênh lệch không đáng kể, đổi lại lần chạy đầy đủ
    # ``pytest --tat-ca`` (351 test) hoàn tất trong ~60s thay vì treo.
    #
    # Lợi ích kèm theo: ``--reuse-db`` trong pytest.ini bây giờ mới thật sự
    # có tác dụng (CSDL trong bộ nhớ thì chẳng có gì để dùng lại). Sau khi
    # sửa model, nhớ chạy lại với ``--create-db`` để dựng lại lược đồ.
    _duong_dan_db = BASE_DIR / ".pytest-db.sqlite3"  # noqa: F405
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(_duong_dan_db),
            "TEST": {"NAME": str(_duong_dan_db)},
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
