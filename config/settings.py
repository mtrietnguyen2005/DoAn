"""
Cấu hình Django cho website quản lý linh kiện điện tử PC/Laptop.
Tài liệu: https://docs.djangoproject.com/en/5.0/ref/settings/
"""
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# BẢO MẬT
# ============================================================================
SECRET_KEY = config("SECRET_KEY", default="django-insecure-doi-secret-key-nay-khi-deploy")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="*", cast=Csv())
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="http://localhost:8000,http://127.0.0.1:8000", cast=Csv())

# ============================================================================
# ỨNG DỤNG
# ============================================================================
INSTALLED_APPS = [
    # Unfold phải đứng trước django.contrib.admin
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.staticfiles",

    # Thư viện bên thứ ba
    "cloudinary",
    "cloudinary_storage",
    "widget_tweaks",

    # Ứng dụng nội bộ
    "apps.core",
    "apps.accounts",
    "apps.catalog",
    "apps.inventory",
    "apps.orders",
    "apps.content",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.shop_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ============================================================================
# CƠ SỞ DỮ LIỆU
# DB_ENGINE=mssql  -> SQL Server (mssql-django)
# DB_ENGINE=sqlite -> SQLite (dùng để chạy thử nhanh, không cần cài SQL Server)
# ============================================================================
DB_ENGINE = config("DB_ENGINE", default="sqlite")

if DB_ENGINE == "mssql":
    _mssql = {
        "ENGINE": "mssql",
        "NAME": config("DB_NAME", default="PCPartsDB"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default=""),
        "OPTIONS": {
            "driver": config("DB_DRIVER", default="ODBC Driver 17 for SQL Server"),
            "extra_params": config("DB_EXTRA_PARAMS", default="TrustServerCertificate=yes"),
        },
    }

    if config("DB_TRUSTED_CONNECTION", default=False, cast=bool):
        # Windows Authentication: dùng chính tài khoản Windows đang đăng nhập,
        # không cần tạo login SQL cũng không cần bật chế độ xác thực hỗn hợp.
        #
        # Lưu ý: mssql-django đọc khoá "Trusted_Connection" (viết hoa T và C) ở
        # CẤP CAO NHẤT của DATABASES chứ không phải trong OPTIONS, và chỉ dùng
        # nó khi USER để trống. Xem mssql/base.py, hàm get_new_connection().
        _mssql["USER"] = ""
        _mssql["PASSWORD"] = ""
        _mssql["Trusted_Connection"] = "yes"
    else:
        # SQL Server Authentication: cần login SQL và bật chế độ xác thực hỗn hợp
        _mssql["USER"] = config("DB_USER", default="")
        _mssql["PASSWORD"] = config("DB_PASSWORD", default="")

    DATABASES = {"default": _mssql}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================================
# XÁC THỰC
# ============================================================================
AUTH_USER_MODEL = "accounts.User"
AUTHENTICATION_BACKENDS = ["apps.accounts.backends.EmailOrUsernameBackend"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

# ============================================================================
# PHIÊN LÀM VIỆC (SESSION)
# ============================================================================
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=60 * 60 * 24 * 14, cast=int)  # 14 ngày
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ============================================================================
# QUỐC TẾ HOÁ
# ============================================================================
LANGUAGE_CODE = "vi"
TIME_ZONE = "Asia/Ho_Chi_Minh"
USE_I18N = True
USE_TZ = True

# ============================================================================
# TỆP TĨNH & MEDIA
# ============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary: bật khi có đủ thông tin cấu hình, ngược lại lưu ảnh trong thư mục media/
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY", default="")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET", default="")
USE_CLOUDINARY = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
    "API_KEY": CLOUDINARY_API_KEY,
    "API_SECRET": CLOUDINARY_API_SECRET,
}

STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USE_CLOUDINARY
            else "django.core.files.storage.FileSystemStorage"
        )
    },
    # Manifest storage chỉ bật khi chạy production (đã chạy collectstatic)
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}

# ============================================================================
# EMAIL (in ra console khi phát triển)
# ============================================================================
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-reply@linhkienpc.vn")

# ============================================================================
# THAM SỐ NGHIỆP VỤ
# ============================================================================
SHOP_NAME = config("SHOP_NAME", default="LinhKienPC")
SHOP_HOTLINE = config("SHOP_HOTLINE", default="1900 6868")
SHOP_EMAIL = config("SHOP_EMAIL", default="hotro@linhkienpc.vn")
SHOP_ADDRESS = config("SHOP_ADDRESS", default="123 Nguyễn Văn Cừ, Quận 5, TP.HCM")

CART_SESSION_KEY = "cart"
DEFAULT_SHIPPING_FEE = config("DEFAULT_SHIPPING_FEE", default=30000, cast=int)
FREE_SHIPPING_THRESHOLD = config("FREE_SHIPPING_THRESHOLD", default=2000000, cast=int)
LOW_STOCK_THRESHOLD = config("LOW_STOCK_THRESHOLD", default=10, cast=int)
EXPIRY_WARNING_DAYS = config("EXPIRY_WARNING_DAYS", default=30, cast=int)

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# ============================================================================
# GIAO DIỆN ADMIN (django-unfold)
# ============================================================================
UNFOLD = {
    "SITE_TITLE": "LinhKienPC Admin",
    "SITE_HEADER": "LinhKienPC · Quản trị",
    "SITE_SUBHEADER": "Hệ thống quản lý linh kiện điện tử PC & Laptop",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "apps.core.dashboard.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "239 246 255", "100": "219 234 254", "200": "191 219 254",
            "300": "147 197 253", "400": "96 165 250", "500": "59 130 246",
            "600": "37 99 235", "700": "29 78 216", "800": "30 64 175",
            "900": "30 58 138", "950": "23 37 84",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Tổng quan",
                "separator": False,
                "items": [
                    {"title": "Bảng điều khiển", "icon": "dashboard", "link": "/admin/"},
                ],
            },
            {
                "title": "Người dùng",
                "separator": True,
                "items": [
                    {"title": "Tài khoản", "icon": "person", "link": "/admin/accounts/user/"},
                    {"title": "Địa chỉ nhận hàng", "icon": "home_pin", "link": "/admin/accounts/address/"},
                    {"title": "Nhóm quyền", "icon": "group", "link": "/admin/auth/group/"},
                ],
            },
            {
                "title": "Sản phẩm",
                "separator": True,
                "items": [
                    {"title": "Sản phẩm", "icon": "memory", "link": "/admin/catalog/product/"},
                    {"title": "Danh mục", "icon": "category", "link": "/admin/catalog/category/"},
                    {"title": "Thương hiệu", "icon": "sell", "link": "/admin/catalog/brand/"},
                    {"title": "Nhà cung cấp", "icon": "local_shipping", "link": "/admin/catalog/supplier/"},
                    {"title": "Đánh giá", "icon": "star", "link": "/admin/catalog/review/"},
                ],
            },
            {
                "title": "Kho hàng",
                "separator": True,
                "items": [
                    {"title": "Lô hàng", "icon": "inventory_2", "link": "/admin/inventory/batch/"},
                    {"title": "Giao dịch kho", "icon": "sync_alt", "link": "/admin/inventory/stocktransaction/"},
                ],
            },
            {
                "title": "Bán hàng",
                "separator": True,
                "items": [
                    {"title": "Đơn hàng", "icon": "receipt_long", "link": "/admin/orders/order/"},
                    {"title": "Vận chuyển", "icon": "local_shipping", "link": "/admin/orders/shipping/"},
                    {"title": "Mã giảm giá", "icon": "confirmation_number", "link": "/admin/orders/promocode/"},
                ],
            },
            {
                "title": "Nội dung",
                "separator": True,
                "items": [
                    {"title": "Banner", "icon": "image", "link": "/admin/content/banner/"},
                    {"title": "Tin tức", "icon": "newspaper", "link": "/admin/content/news/"},
                    {"title": "Khuyến mãi", "icon": "campaign", "link": "/admin/content/promotion/"},
                ],
            },
        ],
    },
}

# ============================================================================
# BẢO MẬT KHI TRIỂN KHAI (chỉ bật khi DEBUG=False và website chạy qua HTTPS)
# ============================================================================
if not DEBUG:
    USE_HTTPS = config("USE_HTTPS", default=True, cast=bool)
    SESSION_COOKIE_SECURE = USE_HTTPS
    CSRF_COOKIE_SECURE = USE_HTTPS
    SECURE_SSL_REDIRECT = USE_HTTPS
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int) if USE_HTTPS else 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS
    SECURE_HSTS_PRELOAD = USE_HTTPS
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
