# 🧪 Tài liệu kiểm thử — LinhKienPC

Bộ kiểm thử được chia làm 3 giai đoạn. **Giai đoạn 1 đã hoàn thành.**

| Giai đoạn | Công nghệ | Trạng thái |
|---|---|---|
| 1. Unit Test | `pytest` + `pytest-django` | ✅ Hoàn thành — 152 test |
| 2. E2E Test | `pytest-playwright` (Page Object Model) | ⏳ Chưa làm |
| 3. API Test | Postman Collection + `newman` | ⚠️ Cần quyết định (xem mục *Vướng mắc*) |

---

## Cài đặt

```bash
pip install -r requirements-dev.txt
```

## Chạy kiểm thử

```bash
pytest                          # chạy toàn bộ
pytest -v                       # hiện tên từng test
pytest tests/unit/test_services.py          # chạy một file
pytest -k "hoan_kho"                        # chạy test có tên chứa từ khoá
pytest -m inventory                         # chạy theo nhóm nghiệp vụ
pytest --cov=apps --cov-report=html         # báo cáo bao phủ (mở htmlcov/index.html)
pytest -n auto                              # chạy song song cho nhanh
```

### Các nhóm test (marker)

| Marker | Phạm vi |
|---|---|
| `unit` | Logic thuần, không cần trình duyệt |
| `inventory` | Nghiệp vụ kho: lô hàng, xuất/nhập/hoàn kho |
| `finance` | Giá vốn COGS, tổng tiền, mã giảm giá |
| `accounts` | Đăng ký, mật khẩu, phân quyền |
| `e2e` | Kiểm thử giao diện (Giai đoạn 2) |

### ⚠️ Chạy test trên SQL Server trước khi nộp

Mặc định test chạy trên SQLite cho nhanh. Nhưng **SQLite dễ tính hơn SQL Server** —
dự án này từng có lỗi `GROUP BY` chỉ xuất hiện trên SQL Server mà SQLite không phát hiện.
Trước khi demo, hãy chạy lại bộ test trên đúng CSDL thật:

```bash
# Windows PowerShell
$env:DB_ENGINE="mssql"; pytest; $env:DB_ENGINE="sqlite"

# macOS / Linux
DB_ENGINE=mssql pytest
```

> Tài khoản CSDL cần quyền `CREATE DATABASE` vì Django tạo database tạm `test_PCPartsDB`.

### Xử lý sự cố khi chạy test

| Triệu chứng | Nguyên nhân & cách khắc phục |
|---|---|
| `collected 0 items` và **không** thấy dòng `configfile: pytest.ini` | Chưa có tệp `pytest.ini` / thư mục `tests/`. Chạy `git pull`. |
| Header báo sai phiên bản Python, `plugins:` thiếu `django` | Lệnh `pytest` trống đang gọi bản pytest cài toàn cục. Dùng `python -m pytest` để bắt buộc dùng Python của môi trường ảo. Kiểm tra bằng `python -c "import sys; print(sys.executable)"`. |
| `ResolutionImpossible ... pytest-playwright depends on pytest<9.0.0` | `pytest` bị ghim phiên bản 9.x. Bộ này ghim `pytest==8.3.5` vì `pytest-playwright` chưa hỗ trợ pytest 9. Chạy `git pull` rồi cài lại. |
| `django.db.utils.OperationalError` khi chạy test | Đổi model nhưng database test cũ còn giữ cấu trúc cũ. Chạy `pytest --create-db`. |

---

## Giai đoạn 1 — Unit Test

### Danh sách tệp

| Tệp | Nội dung | Số test |
|---|---|---|
| `pytest.ini` | Cấu hình pytest, khai báo marker | — |
| `requirements-dev.txt` | Thư viện phục vụ kiểm thử | — |
| `tests/conftest.py` | **Toàn bộ fixtures dữ liệu mẫu** | — |
| `tests/unit/test_models.py` | Logic trong tầng Model | 57 |
| `tests/unit/test_services.py` | Nghiệp vụ kho và đơn hàng | 61 |
| `tests/unit/test_permissions.py` | Phân quyền Read-only trong Admin | 34 |
| | **Tổng** | **152** |

### Danh sách fixtures (`tests/conftest.py`)

**Cấu hình tự động** (`autouse`, không cần khai báo khi dùng)

| Fixture | Tác dụng |
|---|---|
| `fast_password_hashing` | Đổi sang thuật toán băm nhanh, rút ngắn thời gian chạy |
| `media_to_tmp` | Ảnh upload ghi vào thư mục tạm, không đụng `media/` thật |

**Người dùng**

| Fixture | Mô tả |
|---|---|
| `user_factory` | Hàm tạo người dùng tuỳ ý |
| `customer` | Khách hàng thông thường |
| `other_customer` | Khách hàng thứ hai — kiểm tra cách ly dữ liệu |
| `staff_user` | Admin thường (`is_staff`, có đủ permission Django nhưng **không** phải superuser) |
| `superuser` | Toàn quyền |
| `address` | Địa chỉ nhận hàng của `customer` |

**Danh mục sản phẩm**

| Fixture | Mô tả |
|---|---|
| `category`, `brand`, `supplier` | Dữ liệu nền |
| `product_factory` | Hàm tạo sản phẩm tuỳ ý |
| `product` | Sản phẩm 1.500.000đ, **chưa có lô hàng** (tồn kho = 0) |
| `discounted_product` | Sản phẩm 8.000.000đ giảm còn 7.000.000đ |

**Kho hàng** — thiết kế để kiểm thử FIFO

| Fixture | Mô tả |
|---|---|
| `batch_factory` | Hàm tạo lô hàng tuỳ ý |
| `batch_early` | Lô `LO-SOM`: hạn 10 ngày, **4 sản phẩm**, giá vốn 1.000.000đ → phải xuất trước |
| `batch_late` | Lô `LO-MUON`: hạn 200 ngày, **10 sản phẩm**, giá vốn 1.200.000đ |
| `product_with_batches` | Sản phẩm có tổng tồn kho **14** từ hai lô trên |

> Hai lô cố tình đặt **giá vốn khác nhau** để kiểm chứng công thức giá vốn bình quân gia quyền,
> và **hạn sử dụng khác nhau** để kiểm chứng thứ tự xuất kho FIFO.

**Mã giảm giá**

| Fixture | Mô tả |
|---|---|
| `promo_percent` | `GIAM10` — giảm 10%, tối đa 500.000đ |
| `promo_fixed` | `GIAM200K` — giảm 200.000đ, đơn tối thiểu 5.000.000đ |
| `promo_expired` | Mã đã hết hạn |

**Giỏ hàng & đơn hàng**

| Fixture | Mô tả |
|---|---|
| `cart_factory` | Tạo giỏ hàng giả lập: `cart_factory((product, 2))` |
| `order_factory` | Tạo đơn hàng **thật qua service** (có trừ kho, ghi COGS, ghi lịch sử) |
| `order` | Đơn 2 sản phẩm lấy từ lô sớm |

**Nội dung**: `news_article`, `promotion`, `review`

### Dọn dẹp database

`pytest-django` chạy mỗi test trong một transaction riêng và **rollback khi kết thúc**,
nên các test hoàn toàn độc lập, không cần tự tay xoá dữ liệu. Cờ `--reuse-db` trong
`pytest.ini` giữ lại database test giữa các lần chạy để khỏi phải migrate lại từ đầu.
Khi đổi model, chạy `pytest --create-db` để tạo lại.

### Nghiệp vụ đã bao phủ

**Logic kho**
- Tồn kho = tổng số lượng còn lại của tất cả lô
- Xuất kho FIFO: ưu tiên lô hết hạn sớm nhất, lô không có hạn xuất sau cùng
- Lấy tràn sang lô kế tiếp khi lô đầu không đủ
- Ghi vết mọi giao dịch: nhập / xuất / hoàn trả / điều chỉnh, kèm tồn sau giao dịch và người thực hiện
- **Hoàn trả về đúng lô ban đầu khi huỷ đơn** (không dồn sang lô khác)
- Tính nguyên tử: xuất kho thất bại thì tồn kho giữ nguyên, không để lại dữ liệu rác

**Logic tài chính**
- Tổng tiền = (Giá × Số lượng) + Phí ship − Giảm giá
- Miễn phí ship theo ngưỡng cấu hình
- Mã giảm theo phần trăm (có trần) và theo số tiền cố định
- Số tiền giảm không vượt quá giá trị đơn
- **Lưu giá vốn COGS tại thời điểm bán**, bình quân gia quyền khi lấy từ nhiều lô
- Giá vốn đã lưu **không đổi** khi nhập lô mới giá khác
- Hoàn lại lượt dùng mã giảm giá khi huỷ đơn

**Logic người dùng**
- Mật khẩu không bao giờ lưu dạng văn bản thô, băm bằng `pbkdf2_sha256` trong cấu hình production
- Email là duy nhất
- Chỉ tồn tại duy nhất một địa chỉ mặc định cho mỗi người dùng
- Địa chỉ của hai người dùng không ảnh hưởng nhau
- **Phân quyền Read-only**: Địa chỉ, Đánh giá, Giao dịch kho — Admin thường chỉ xem được
  (kiểm chứng cả ở tầng `ModelAdmin` lẫn qua HTTP thật), superuser giữ toàn quyền

### Độ bao phủ logic nghiệp vụ cốt lõi

```
apps/orders/services.py       100%
apps/inventory/services.py     96%
apps/orders/models.py          96%
apps/catalog/models.py         93%
apps/accounts/models.py        92%
apps/core/admin_mixins.py     100%
                       TỔNG    95%
```

---

## Hai lỗi thật được phát hiện nhờ Giai đoạn 1

Bộ test này không chỉ để "có test" — nó đã tìm ra hai lỗi có thật trong mã nguồn:

**1. Thứ tự họ tên sai với tiếng Việt.** `User.display_name` dùng `get_full_name()` của Django
(ghép `first_name + last_name` theo kiểu phương Tây) nên hiển thị *"An Nguyễn"* thay vì
*"Nguyễn An"*, trong khi biểu mẫu lại đặt nhãn `last_name = "Họ"`, `first_name = "Tên"`.
→ Đã ghi đè `get_full_name()` để ghép đúng thứ tự Họ + Tên.

**2. Đối tượng trong bộ nhớ lệch với database.** `Address.save()` đặt địa chỉ mặc định bằng
`.update()`, vốn chỉ ghi xuống database mà không cập nhật đối tượng Python đang giữ. Ai gọi
`Address.objects.create(...)` rồi đọc `.is_default` ngay sau đó sẽ nhận giá trị sai.
→ Đã gán lại `self.is_default = True` cho đồng bộ.

---

## Vướng mắc cần quyết định

### Giai đoạn 3 (Postman) chưa thực hiện được

Dự án **không có REST API**. Toàn bộ là Django Templates render HTML phía server, chỉ có
**3 endpoint trả JSON**, đều thuộc giỏ hàng (`/gio-hang/dong-bo/`, `/gio-hang/so-luong/`,
`/gio-hang/them/<id>/`). Không có `djangorestframework`, không có JWT — xác thực bằng
**session cookie + CSRF token**.

Đây không phải lỗi: kiến trúc này do yêu cầu ban đầu quy định (Django Templates + HTMX),
vốn không cần API. Ba lựa chọn:

| Phương án | Việc phải làm |
|---|---|
| **A. Xây tầng REST API** *(đề xuất)* | Cài `djangorestframework` + `simplejwt`, viết Serializer/ViewSet cho Auth, Products, Orders, Warehouse. Sau đó Postman test đúng như mô tả: JWT Bearer, JSON schema validation |
| **B. Test endpoint HTML hiện có** | Postman kiểm tra status code, redirect, session cookie. **Không có** JWT, không validate JSON schema |
| **C. Bỏ Giai đoạn 3** | Chỉ làm Unit Test + Playwright |

### Hai bộ test đang song song tồn tại

Bộ cũ kiểu `django.test.TestCase` vẫn nằm ở `apps/*/tests.py` (62 test, chạy bằng
`python manage.py test`). Bộ mới dùng `pytest` nằm ở `tests/`. `pytest.ini` đặt
`testpaths = tests` nên hai bộ không lẫn nhau.

Đề xuất: sau khi xong Giai đoạn 2, **di chuyển nốt phần còn thiếu và xoá `apps/*/tests.py`**
để chỉ còn một bộ duy nhất.
