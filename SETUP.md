# 📘 Hướng dẫn cài đặt từng bước — LinhKienPC

Tài liệu này hướng dẫn cài đặt và chạy website từ con số 0. Làm **tuần tự từ Bước 1 đến Bước 9**.

> 💡 **Muốn chạy thử thật nhanh?** Bạn có thể **bỏ qua Bước 3 (SQL Server)** và **Bước 7 (Cloudinary)** bằng cách
> đặt `DB_ENGINE=sqlite` trong tệp `.env`. Website vẫn chạy đầy đủ chức năng, chỉ khác là dùng SQLite
> và lưu ảnh trong thư mục `media/`. Khi nào cần nộp/demo với SQL Server thì quay lại làm 2 bước đó.

---

## Bước 1 — Cài đặt Python

> ⛔ **Bắt buộc dùng Python 3.11 hoặc 3.12. KHÔNG dùng 3.13 / 3.14.**
> Django 5.0 chỉ hỗ trợ chính thức Python 3.10–3.12. Ngoài ra hai gói `Pillow` và `pyodbc`
> chưa có bản dựng sẵn (wheel) cho Python 3.14, nên `pip` sẽ phải biên dịch từ mã nguồn C
> và báo lỗi `Microsoft Visual C++ 14.0 or greater is required`.
> **Cài đúng Python 3.12 là hết lỗi này, không cần tải C++ Build Tools.**

1. Tải Python **3.12** tại <https://www.python.org/downloads/release/python-31210/>
   → kéo xuống cuối trang, chọn **Windows installer (64-bit)**.
2. Khi cài trên Windows, **bắt buộc tích vào ô `Add python.exe to PATH`** ở màn hình đầu tiên.
3. Mở Command Prompt / PowerShell / Terminal và kiểm tra:

```bash
python --version
```

Kết quả mong đợi: `Python 3.12.x`. Nếu máy báo không tìm thấy lệnh, hãy thử `python3 --version`.

> 💡 **Máy đã lỡ cài sẵn Python 3.13/3.14 rồi?** Không cần gỡ. Cứ cài thêm 3.12 rồi ở Bước 2
> tạo môi trường ảo bằng lệnh `py -3.12 -m venv .venv` — bộ khởi chạy `py` của Windows sẽ
> chọn đúng phiên bản bạn chỉ định.

---

## Bước 2 — Tải mã nguồn và tạo môi trường ảo

```bash
# Tải mã nguồn
git clone https://github.com/mtrietnguyen2005/DoAn.git
cd DoAn

# Tạo môi trường ảo (venv)
python -m venv .venv

# Nếu máy có nhiều phiên bản Python, hãy chỉ định rõ 3.12 (Windows):
#   py -3.12 -m venv .venv
```

> ⚠️ **Phải `cd` vào thư mục dự án TRƯỚC KHI tạo môi trường ảo.** Nếu dấu nhắc lệnh vẫn còn là
> `C:\Users\<tên bạn>` thì bạn đang đứng sai chỗ, và lệnh `pip install -r requirements.txt`
> ở Bước 4 sẽ báo `Could not open requirements file`. Dấu nhắc đúng phải có tên thư mục dự án,
> ví dụ `PS T:\DoAn>`.

**Kích hoạt môi trường ảo:**

| Hệ điều hành | Lệnh |
|---|---|
| Windows (CMD) | `.venv\Scripts\activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| macOS / Linux | `source .venv/bin/activate` |

> ⚠️ Nếu PowerShell báo lỗi *"running scripts is disabled"*, chạy lệnh sau rồi thử lại:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Khi kích hoạt thành công, đầu dòng lệnh sẽ có chữ `(.venv)`. **Mọi lệnh phía sau đều chạy trong môi trường này.**

---

## Bước 3 — Cài đặt SQL Server và ODBC Driver

> Bỏ qua bước này nếu bạn dùng SQLite (`DB_ENGINE=sqlite`).

### 3.1. Cài SQL Server

Tải **SQL Server Express** (miễn phí) tại <https://www.microsoft.com/sql-server/sql-server-downloads> → chọn bản **Express** → **Basic**.

Nên cài thêm **SQL Server Management Studio (SSMS)** để thao tác với cơ sở dữ liệu bằng giao diện:
<https://learn.microsoft.com/sql/ssms/download-sql-server-management-studio-ssms>

### 3.2. Cài ODBC Driver (bắt buộc — thư viện `pyodbc` cần driver này)

Tải **ODBC Driver 17 for SQL Server** tại:
<https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server>

Kiểm tra driver đã cài (Windows): mở **ODBC Data Sources (64-bit)** → tab **Drivers** → phải thấy `ODBC Driver 17 for SQL Server`.

### 3.3. Bật xác thực SQL và TCP/IP

> ⚠️ **Trước tiên hãy xem bạn có mấy instance SQL Server.**
> Mở **SQL Server Configuration Manager** → `SQL Server Services`. Nếu trong danh sách đã có
> một dòng đang ở trạng thái **Running** (ví dụ `SQL Server (MSSQLSERVER)`), **hãy dùng luôn instance đó**
> và bỏ qua toàn bộ phần cấu hình SQLEXPRESS bên dưới. Máy bạn có thể cài sẵn nhiều instance
> (thường do đã cài Visual Studio hoặc SQL Server bản đầy đủ từ trước).
>
> - Instance mặc định `MSSQLSERVER` → trong `.env` điền `DB_HOST=localhost` và `DB_PORT=1433`
> - Instance `SQLEXPRESS` → trong `.env` điền `DB_HOST=localhost\SQLEXPRESS`, **để trống** `DB_PORT`
>
> **Tuyệt đối không đặt hai instance cùng dùng cổng 1433.** Cổng chỉ thuộc về một tiến trình:
> instance thứ hai sẽ không khởi động được và Configuration Manager báo lỗi
> *"The request failed or the service did not respond in a timely fashion"*.

1. Mở **SSMS**, kết nối vào server → chuột phải tên server → **Properties** → **Security** →
   chọn **SQL Server and Windows Authentication mode** → OK.
2. Mở **SQL Server Configuration Manager** →
   `SQL Server Network Configuration` → `Protocols for <tên instance của bạn>` → bật **TCP/IP** (Enabled).
3. Chuột phải **TCP/IP** → **Properties** → tab **IP Addresses** → kéo xuống mục `IPAll`:
   - Nếu đây là instance **duy nhất** trên máy → đặt **TCP Port = `1433`**.
   - Nếu máy **đã có instance khác đang chiếm cổng 1433** → đặt một cổng khác, ví dụ **`1434`**,
     rồi khai báo đúng cổng đó trong `.env` (`DB_PORT=1434`).
4. Vào `SQL Server Services` → chuột phải đúng instance của bạn → **Restart**.

> 🔎 **Service không khởi động lên được?** Mở tệp nhật ký lỗi của SQL Server:
> `C:\Program Files\Microsoft SQL Server\MSSQL##.<TÊN_INSTANCE>\MSSQL\Log\ERRORLOG`
> (`##` là số phiên bản, ví dụ `MSSQL16.SQLEXPRESS`). Tìm dòng chứa `TCP port` hoặc
> `Only one usage of each socket address` — đó chính là dấu hiệu trùng cổng.

### 3.4. Tạo cơ sở dữ liệu

Trong SSMS, mở **New Query** và chạy:

```sql
CREATE DATABASE PCPartsDB
COLLATE Vietnamese_CI_AS;
GO
```

> `Vietnamese_CI_AS` giúp tìm kiếm tiếng Việt không phân biệt hoa/thường chính xác hơn.

**Tạo tài khoản đăng nhập riêng cho ứng dụng** (khuyến nghị, an toàn hơn dùng `sa`):

```sql
CREATE LOGIN pcparts_user WITH PASSWORD = 'MatKhauManh@123';
GO
USE PCPartsDB;
GO
CREATE USER pcparts_user FOR LOGIN pcparts_user;
ALTER ROLE db_owner ADD MEMBER pcparts_user;
GO
```

---

## Bước 4 — Cài đặt các thư viện Python

Đảm bảo môi trường ảo đang bật `(.venv)`, sau đó chạy:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> 🐧 **Lỗi khi cài `pyodbc` trên macOS/Linux?** Cần cài thư viện hệ thống trước:
> - Ubuntu/Debian: `sudo apt-get install -y unixodbc-dev`
> - macOS: `brew install unixodbc`
>
> 🪟 **Lỗi "Microsoft Visual C++ 14.0 is required" trên Windows?**
> Cài **Microsoft C++ Build Tools**: <https://visualstudio.microsoft.com/visual-cpp-build-tools/>
>
> Nếu vẫn không cài được `pyodbc`, hãy tạm dùng `DB_ENGINE=sqlite` để tiếp tục các bước sau.

---

## Bước 5 — Tạo tệp cấu hình `.env`

Sao chép tệp mẫu:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Mở tệp `.env` vừa tạo bằng trình soạn thảo và sửa các dòng cho khớp với máy của bạn:

```ini
SECRET_KEY=hay-doi-thanh-mot-chuoi-ngau-nhien-that-dai
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# --- Cơ sở dữ liệu ---
DB_ENGINE=mssql
DB_NAME=PCPartsDB
DB_USER=pcparts_user
DB_PASSWORD=MatKhauManh@123
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_EXTRA_PARAMS=TrustServerCertificate=yes
DB_TRUSTED_CONNECTION=False
```

**Ghi chú quan trọng:**

| Trường hợp | Cách điền |
|---|---|
| Dùng SQLite cho nhanh | `DB_ENGINE=sqlite` (các dòng `DB_*` khác bỏ qua) |
| SQL Server bản Express có tên instance | `DB_HOST=localhost\SQLEXPRESS` và **để trống** `DB_PORT` |
| Dùng Windows Authentication | `DB_TRUSTED_CONNECTION=True`, để trống `DB_USER` và `DB_PASSWORD` |
| Đã cài ODBC Driver 18 | `DB_DRIVER=ODBC Driver 18 for SQL Server` |

Tạo `SECRET_KEY` ngẫu nhiên (chạy trong terminal đang bật venv):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Chép chuỗi in ra vào dòng `SECRET_KEY=` trong `.env`.

---

## Bước 6 — Tạo bảng trong cơ sở dữ liệu

```bash
python manage.py migrate
```

Kết quả mong đợi: một loạt dòng `Applying ... OK`.

> ❌ **Lỗi `Login failed for user`** → sai `DB_USER` / `DB_PASSWORD`, hoặc chưa bật *SQL Server Authentication mode* (mục 3.3).
> ❌ **Lỗi `Data source name not found`** → tên driver trong `DB_DRIVER` không khớp với driver đã cài (kiểm tra lại mục 3.2).
> ❌ **Lỗi `TCP Provider: No connection could be made`** → chưa bật TCP/IP hoặc chưa restart dịch vụ SQL Server (mục 3.3).

---

## Bước 7 — Cấu hình Cloudinary (tùy chọn)

Nếu **bỏ qua** bước này, ảnh sẽ được lưu trong thư mục `media/` trên máy — website vẫn chạy bình thường.

1. Đăng ký tài khoản miễn phí tại <https://cloudinary.com/users/register_free>.
2. Vào **Dashboard**, sao chép 3 giá trị: `Cloud name`, `API Key`, `API Secret`.
3. Điền vào `.env`:

```ini
CLOUDINARY_CLOUD_NAME=ten-cloud-cua-ban
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcXYZ_khoa_bi_mat
```

Hệ thống **tự động phát hiện**: có đủ 3 giá trị → dùng Cloudinary; thiếu bất kỳ giá trị nào → lưu vào `media/`.

---

## Bước 8 — Tạo dữ liệu mẫu và tài khoản quản trị

### 8.1. Tạo dữ liệu mẫu (khuyến nghị)

```bash
python manage.py seed_data
```

Lệnh này tạo sẵn: 10 danh mục, 12 thương hiệu, 4 nhà cung cấp, 20 sản phẩm kèm lô hàng,
25 đánh giá, 4 bài tin tức, 1 chương trình khuyến mãi và 2 mã giảm giá.

Tài khoản được tạo kèm:

| Vai trò | Tên đăng nhập | Mật khẩu |
|---|---|---|
| Quản trị viên | `admin` | `admin123456` |
| Khách hàng | `khachhang1` … `khachhang5` | `khachhang123` |

> Muốn xóa hết dữ liệu mẫu cũ và tạo lại: `python manage.py seed_data --reset`

### 8.2. Hoặc tự tạo tài khoản quản trị

```bash
python manage.py createsuperuser
```

Nhập lần lượt: tên đăng nhập, email, mật khẩu (mật khẩu tối thiểu 8 ký tự, không được toàn số).

---

## Bước 9 — Khởi chạy website

```bash
python manage.py runserver
```

Mở trình duyệt và truy cập:

| Trang | Địa chỉ |
|---|---|
| 🏠 Trang chủ | <http://127.0.0.1:8000> |
| 🛍️ Danh sách sản phẩm | <http://127.0.0.1:8000/san-pham/> |
| 🛒 Giỏ hàng | <http://127.0.0.1:8000/gio-hang/> |
| 📦 Đơn hàng của tôi | <http://127.0.0.1:8000/gio-hang/don-hang/> |
| ⚙️ **Trang quản trị** | <http://127.0.0.1:8000/admin/> |

Dừng server: nhấn `Ctrl + C`.

---

## 🧪 Kịch bản kiểm thử nhanh (để demo đồ án)

Chạy tuần tự để thấy toàn bộ nghiệp vụ cốt lõi hoạt động:

1. **Đăng nhập khách hàng** — vào `/tai-khoan/dang-nhap/`, đăng nhập bằng `khachhang1 / khachhang123`.
2. **Ghi lại tồn kho** — mở `/admin/catalog/product/`, xem cột **Tồn kho** của một sản phẩm bất kỳ.
3. **Đặt hàng** — thêm sản phẩm đó vào giỏ, vào giỏ hàng, nhập mã `CHAOBAN`, bấm **Tiến hành đặt hàng**, điền địa chỉ và **Đặt hàng ngay**.
4. **Kiểm tra trừ kho** — quay lại `/admin/catalog/product/`: tồn kho đã **giảm đúng số lượng đã mua**.
5. **Kiểm tra giá vốn (COGS)** — mở `/admin/orders/order/` → vào đơn vừa tạo → phần *Chi tiết đơn hàng*
   hiển thị `Đơn giá bán`, `Giá vốn (COGS)`, `Lợi nhuận` của từng dòng và của cả đơn.
6. **Kiểm tra nhật ký kho** — mở `/admin/inventory/stocktransaction/`: có bản ghi **Xuất kho (bán hàng)**
   với số lượng âm, kèm mã lô và tồn kho sau giao dịch.
7. **Đổi trạng thái** — trong trang đơn hàng, đổi trạng thái sang *Đã xác nhận*, lưu lại → phần
   *Lịch sử trạng thái đơn* tự động ghi thêm một dòng.
8. **Hủy đơn & hoàn kho** — quay lại giao diện khách, mở `/gio-hang/don-hang/`, vào đơn vừa đặt,
   bấm **Xác nhận hủy đơn**. Kiểm tra lại:
   - Tồn kho sản phẩm **trở về đúng con số ban đầu**.
   - `/admin/inventory/batch/`: số lượng được cộng lại **vào đúng lô đã xuất**, không dồn sang lô khác.
   - `/admin/inventory/stocktransaction/`: có thêm giao dịch **Hoàn trả (hủy đơn)**.
9. **Đánh giá sản phẩm** — vào trang chi tiết sản phẩm, viết đánh giá, sau đó **sửa** và **xóa** để kiểm tra CRUD.
10. **Kiểm tra phân quyền read-only** — tạo một user mới trong `/admin/accounts/user/`, tích `is_staff`
    (**không** tích `is_superuser`), cấp quyền cho user đó rồi đăng nhập bằng tài khoản này:
    mục **Địa chỉ**, **Đánh giá**, **Giao dịch kho** chỉ xem được, không có nút *Thêm/Sửa/Xóa*.

Chạy toàn bộ bộ kiểm thử tự động (59 test):

```bash
python manage.py test
```

---

## 🚀 Triển khai lên máy chủ (production)

Khi đưa lên server thật, cần đổi các mục sau trong `.env`:

```ini
DEBUG=False
ALLOWED_HOSTS=tenmiencuaban.com,www.tenmiencuaban.com
CSRF_TRUSTED_ORIGINS=https://tenmiencuaban.com
SECRET_KEY=mot-chuoi-bi-mat-hoan-toan-moi
```

Sau đó thu thập tệp tĩnh và chạy bằng WSGI server:

```bash
python manage.py collectstatic --noinput
python manage.py migrate
pip install gunicorn                     # Linux
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

> Trên Windows dùng `waitress` thay cho `gunicorn`:
> `pip install waitress` rồi `waitress-serve --port=8000 config.wsgi:application`

---

## ❓ Xử lý sự cố thường gặp

| Thông báo lỗi | Nguyên nhân & cách khắc phục |
|---|---|
| `Microsoft Visual C++ 14.0 or greater is required` / `Failed to build Pillow pyodbc` | Đang dùng Python 3.13/3.14 — các gói chưa có wheel dựng sẵn nên phải biên dịch. Cài Python 3.12 rồi tạo lại venv bằng `py -3.12 -m venv .venv` (xem Bước 1). |
| `Could not open requirements file: 'requirements.txt'` | Đang đứng sai thư mục. Chạy `cd T:\DoAn` (hoặc đường dẫn dự án của bạn), kiểm tra bằng `dir requirements.txt` rồi cài lại. |
| `ModuleNotFoundError: No module named 'django'` | Chưa kích hoạt môi trường ảo. Chạy lại lệnh activate ở Bước 2. |
| `django.db.utils.InterfaceError: ('IM002'...)` | Chưa cài ODBC Driver, hoặc `DB_DRIVER` sai tên (mục 3.2). |
| `Login failed for user 'sa'` | Sai mật khẩu, hoặc chưa bật SQL Server Authentication (mục 3.3). |
| Service SQL Server không Start được, báo *"did not respond in a timely fashion"* | Nhiều khả năng hai instance trùng cổng 1433. Xem lại khung cảnh báo ở mục 3.3 và tệp `ERRORLOG`. |
| `Cannot open database "PCPartsDB"` | Chưa tạo database. Chạy lại câu lệnh `CREATE DATABASE` ở mục 3.4. |
| `no such table: accounts_user` | Chưa chạy `python manage.py migrate` (Bước 6). |
| Trang web không có định dạng CSS | Máy không vào được Internet (Tailwind & HTMX tải qua CDN). Kiểm tra kết nối mạng. |
| Ảnh tải lên không hiển thị | Chưa cấu hình Cloudinary và đang chạy `DEBUG=False`. Đặt `DEBUG=True` khi phát triển. |
| `Port 8000 is already in use` | Chạy cổng khác: `python manage.py runserver 8001` |
| Lỡ quên mật khẩu admin | `python manage.py changepassword admin` |
