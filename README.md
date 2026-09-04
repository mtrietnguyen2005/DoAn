# 🖥️ LinhKienPC — Website quản lý linh kiện điện tử PC & Laptop

Đồ án website thương mại điện tử chuyên bán linh kiện máy tính (CPU, VGA, RAM, SSD, Mainboard, Laptop…)
với hệ thống **quản lý tồn kho theo lô hàng**, truy vết giao dịch kho và tính lợi nhuận theo giá vốn thực tế.

> 📘 **Hướng dẫn cài đặt chi tiết từng bước có trong tệp [SETUP.md](SETUP.md).**

---

## 1. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend & Frontend | **Python 3.11 hoặc 3.12** / **Django 5.0** (Django Templates) |
| Tương tác động | **HTMX 1.9** (lọc sản phẩm, giỏ hàng không tải lại trang) |
| Giao diện | **TailwindCSS 3** (qua CDN) |
| Cơ sở dữ liệu | **SQL Server** qua `mssql-django` (có thể chuyển SQLite để chạy thử) |
| Trang quản trị | **Django Admin** tùy biến bằng `django-unfold` |
| Lưu trữ ảnh | **Cloudinary** (`django-cloudinary-storage`), tự chuyển về thư mục `media/` nếu chưa cấu hình |

## 2. Cấu trúc dự án

```
DoAn/
├── config/                     # Cấu hình Django (settings, urls, wsgi, asgi)
├── apps/
│   ├── accounts/               # User, Address, đăng nhập bằng username hoặc email
│   ├── catalog/                # Category, Brand, Supplier, Product, ProductImage, Review
│   ├── inventory/              # Batch (lô hàng), StockTransaction + services.py (FIFO, hoàn kho)
│   ├── orders/                 # Cart, Order, OrderItem, OrderItemBatch, Shipping, PromoCode
│   ├── content/                # Banner, News, Promotion
│   └── core/                   # Trang chủ, dashboard admin, template tags, seed_data
├── templates/                  # Toàn bộ giao diện (Django Templates + Tailwind)
├── static/                     # CSS, JS (giỏ hàng LocalStorage)
├── requirements.txt
├── .env.example                # Mẫu biến môi trường
├── SETUP.md                    # ⭐ Hướng dẫn cài đặt từng bước
└── manage.py
```

## 3. Chức năng chính

### 3.1. Khách hàng
- Đăng ký / đăng nhập (bằng **tên đăng nhập hoặc email**) / đăng xuất, tùy chọn "ghi nhớ đăng nhập".
- Cập nhật hồ sơ, ảnh đại diện, đổi mật khẩu.
- Quản lý danh sách địa chỉ nhận hàng (thêm/sửa/xóa/đặt mặc định).
- Xem, **tìm kiếm và lọc sản phẩm** theo danh mục, thương hiệu, khoảng giá, còn hàng, đang giảm giá — lọc bằng HTMX không tải lại trang.
- Xem banner, chương trình khuyến mãi, tin tức công nghệ, danh sách nhà cung cấp.
- Giỏ hàng lưu **LocalStorage + Session**, tự động đồng bộ lên tài khoản khi đăng nhập.
- Áp dụng mã giảm giá, đặt hàng **COD**, miễn phí vận chuyển theo ngưỡng cấu hình.
- Xem lịch sử đơn hàng, chi tiết đơn, **lịch sử thay đổi trạng thái** và **hủy đơn khi chưa giao**.
- Đánh giá sản phẩm đầy đủ **CRUD** (mỗi khách 1 đánh giá / 1 sản phẩm).

### 3.2. Quản trị viên — `/admin`
- Quản lý toàn bộ model: User, Address, Product, Category, Brand, Supplier, Batch, StockTransaction, Order, OrderItem, Shipping, PromoCode, News, Banner, Promotion.
- **Dashboard**: tổng số User / Sản phẩm / Đơn hàng / Đánh giá, doanh thu và lợi nhuận tháng, đơn hàng theo trạng thái, **danh sách lô hàng sắp hết hạn** và **sản phẩm sắp hết tồn kho**.
- Đổi trạng thái đơn hàng ngay trên trang admin (kể cả hàng loạt) — luôn đi qua service để ghi lịch sử và hoàn kho.
- **Phân quyền chỉ đọc (read-only)** với Admin thường ở 3 resource: **Địa chỉ người dùng**, **Đánh giá**, **Giao dịch kho**. Chỉ superuser mới được thêm/sửa/xóa.

### 3.3. Logic kho & đơn hàng (phần cốt lõi)
- **Tồn kho theo lô** (`Batch`): tồn kho sản phẩm = tổng số lượng còn lại của tất cả lô.
- **Xuất kho FIFO**: ưu tiên lô có hạn sử dụng sớm nhất, sau đó đến ngày nhập kho.
- **Sổ nhật ký kho** (`StockTransaction`): ghi vết mọi giao dịch Nhập / Xuất / Hoàn trả / Điều chỉnh thủ công, kèm tồn kho sau giao dịch và người thực hiện.
- **Lưu giá vốn (COGS)** vào `OrderItem.cost_price` tại thời điểm bán (bình quân gia quyền khi lấy từ nhiều lô) → tính lợi nhuận chính xác kể cả khi giá nhập thay đổi sau này.
- **Bảng phân bổ lô** (`OrderItemBatch`) ghi rõ mỗi dòng hàng lấy bao nhiêu từ lô nào → khi hủy đơn, số lượng được **hoàn trả về đúng lô ban đầu**, không dồn vào một lô.
- **Lịch sử trạng thái đơn** (`OrderStatusHistory`): Chờ xác nhận → Đã xác nhận → Đang giao → Hoàn thành → Hủy.

## 4. Cài đặt nhanh

> ⛔ Yêu cầu **Python 3.11 hoặc 3.12** — không dùng 3.13/3.14 (xem lý do ở [SETUP.md](SETUP.md) Bước 1).

```bash
python -m venv .venv             # Windows nhiều bản Python: py -3.12 -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env
python manage.py migrate
python manage.py seed_data       # tạo dữ liệu mẫu
python manage.py runserver
```

Mở trình duyệt: <http://127.0.0.1:8000> · Trang quản trị: <http://127.0.0.1:8000/admin>

**Tài khoản mẫu** (do `seed_data` tạo):

| Vai trò | Tên đăng nhập | Mật khẩu |
|---|---|---|
| Quản trị viên | `admin` | `admin123456` |
| Khách hàng | `khachhang1` … `khachhang5` | `khachhang123` |

**Mã giảm giá mẫu:** `CHAOBAN` (giảm 5%, tối đa 500.000đ) · `GIAM200K` (giảm 200.000đ cho đơn từ 5 triệu)

## 5. Chạy kiểm thử

Xem tài liệu đầy đủ ở **[TESTING.md](TESTING.md)**.

```bash
pip install -r requirements-dev.txt
playwright install chromium   # chỉ cần cho E2E, chạy một lần

pytest                        # 231 test Unit + Integration (~4 giây)
pytest -m e2e                 # 45 test E2E bằng trình duyệt thật (~40 giây)
pytest -m ""                  # tất cả 276 test
pytest --cov=apps             # kèm báo cáo độ bao phủ
```

| Loại | Số test | Phạm vi |
|---|---|---|
| Unit | 152 | Logic model và service: FIFO, hoàn kho đúng lô, COGS, mã giảm giá, phân quyền |
| Integration | 79 | Qua HTTP: đăng ký/đăng nhập, lọc sản phẩm, giỏ hàng, đặt hàng, dashboard |
| E2E | 45 | Trình duyệt thật (Playwright + Page Object Model): luồng khách hàng và quản trị |

Bao phủ **95%** logic nghiệp vụ cốt lõi (`orders/services.py` đạt 100%).
