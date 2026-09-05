# 🧪 Tài liệu kiểm thử — LinhKienPC

Bộ kiểm thử được chia làm 3 giai đoạn. **Giai đoạn 1 đã hoàn thành.**

| Giai đoạn | Công nghệ | Trạng thái |
|---|---|---|
| 1. Unit Test | `pytest` + `pytest-django` | ✅ Hoàn thành — 152 test |
| 1b. Integration | `pytest-django` (qua HTTP) | ✅ Hoàn thành — 96 test |
| 2. E2E Test | `pytest-playwright` (Page Object Model) | ✅ Hoàn thành — 45 test |
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
| `integration` | Kiểm thử qua HTTP, không cần trình duyệt |
| `e2e` | Kiểm thử giao diện bằng trình duyệt thật (Giai đoạn 2) |

### Test chạy trên CSDL nào?

Bộ test dùng cấu hình riêng `config/settings_test.py`, **mặc định chạy SQLite trong bộ nhớ**
bất kể `.env` của bạn đặt `DB_ENGINE` là gì. Lý do:

* Nhanh hơn nhiều lần (toàn bộ 152 test chạy trong ~2 giây)
* Không đụng tới database thật
* Ai clone dự án về cũng chạy được ngay, không cần cài SQL Server

### ⚠️ Chạy test trên SQL Server trước khi nộp

**SQLite dễ tính hơn SQL Server** — dự án này từng có lỗi `GROUP BY` chỉ xuất hiện trên
SQL Server mà SQLite hoàn toàn không phát hiện. Nên chạy lại ít nhất một lần trên CSDL thật:

```powershell
# Windows PowerShell
$env:TEST_ON_MSSQL="True"; python -m pytest; $env:TEST_ON_MSSQL="False"
```

```bash
# macOS / Linux
TEST_ON_MSSQL=True pytest
```

> **Yêu cầu quyền:** Django phải tạo database tạm `test_PCPartsDB`, nên tài khoản CSDL
> cần quyền tạo database. Nếu dùng Windows Authentication (`DB_TRUSTED_CONNECTION=True`)
> và bạn là người cài SQL Server thì thường đã có sẵn quyền này.
> Nếu dùng login SQL riêng, cấp quyền bằng SSMS:
>
> ```sql
> ALTER SERVER ROLE dbcreator ADD MEMBER [pcparts_user];
> ```

### Xử lý sự cố khi chạy test

| Triệu chứng | Nguyên nhân & cách khắc phục |
|---|---|
| `collected 0 items` và **không** thấy dòng `configfile: pytest.ini` | Chưa có tệp `pytest.ini` / thư mục `tests/`. Chạy `git pull`. |
| Header báo sai phiên bản Python, `plugins:` thiếu `django` | Lệnh `pytest` trống đang gọi bản pytest cài toàn cục. Dùng `python -m pytest` để bắt buộc dùng Python của môi trường ảo. Kiểm tra bằng `python -c "import sys; print(sys.executable)"`. |
| `ResolutionImpossible ... pytest-playwright depends on pytest<9.0.0` | `pytest` bị ghim phiên bản 9.x. Bộ này ghim `pytest==8.3.5` vì `pytest-playwright` chưa hỗ trợ pytest 9. Chạy `git pull` rồi cài lại. |
| Toàn bộ test lỗi `Login failed for user` khi chạy trên SQL Server | Tài khoản chưa có quyền tạo database tạm `test_PCPartsDB`. SQL Server báo mã 18456 kể cả khi login đúng nhưng không mở được database. Cấp quyền `dbcreator` (xem trên), hoặc bỏ `TEST_ON_MSSQL` để chạy trên SQLite. |
| `django.db.utils.OperationalError` khi chạy test | Đổi model nhưng database test cũ còn giữ cấu trúc cũ. Chạy `pytest --create-db`. |

---

## Giai đoạn 1 — Unit Test

### Danh sách tệp

| Tệp | Nội dung | Số test |
|---|---|---|
| `pytest.ini` | Cấu hình pytest, khai báo marker | — |
| `config/settings_test.py` | Cấu hình riêng khi test (mặc định SQLite trong bộ nhớ) | — |
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

### Tổng số test

```
Unit          152    (tests/unit/)
Integration    96    (tests/integration/)
E2E            45    (tests/e2e/)
             -----
TỔNG          293
```

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

## Năm lỗi thật được phát hiện nhờ Giai đoạn 2

**0. Ghi chú template hiện ra trang web như văn bản.**
Django chỉ hỗ trợ `{# ... #}` trên **một dòng**. Bốn ghi chú nhiều dòng thêm vào
`base.html`, `product_grid.html`, `product_list.html` và `cart_summary.html` không
được coi là ghi chú mà in thẳng ra đầu mỗi trang. → Đã đổi sang
`{% comment %} ... {% endcomment %}` và bổ sung `tests/integration/test_templates.py`
quét toàn bộ template lẫn HTML render ra.


**1. 🔴 Khách vãng lai không thêm được hàng vào giỏ (nghiêm trọng).**
Trang chủ và trang danh sách sản phẩm không có form POST nào dành cho khách chưa
đăng nhập, nên `base.html` không phát hành CSRF token và Django cũng không đặt
cookie `csrftoken`. Hàm `getCsrfToken()` trong `cart.js` trả về chuỗi rỗng, POST
"Thêm vào giỏ" bị chặn với lỗi 403. **Toàn bộ khách chưa đăng nhập không mua được
hàng.** → Đã thêm `<meta name="csrf-token">` vào `base.html`.

> Vì sao bộ test tích hợp không bắt được? `django.test.Client` **mặc định tắt
> kiểm tra CSRF**. Chỉ trình duyệt thật mới lộ ra lỗi này. Đã bổ sung
> `TestCsrfChoKhachVangLai` dùng `Client(enforce_csrf_checks=True)` để lần sau
> bắt được mà không cần trình duyệt.

**2. Giỏ hàng hỏng hoàn toàn nếu HTMX không tải được.**
Các form tăng/giảm số lượng, xoá sản phẩm và xoá toàn bộ giỏ chỉ có thuộc tính
`hx-post`, thiếu `method` và `action`. Nếu mạng chậm hoặc CDN lỗi, khách không sửa
được gì trong giỏ. → Đã bổ sung `method="post"` và `action` làm phương án dự phòng.

**3. Sắp xếp sản phẩm cũng hỏng khi thiếu HTMX.**
Ô "Sắp xếp" nằm trong một `<form>` không có `method`/`action`, và `onchange` gọi
thẳng `htmx.trigger()` — thiếu HTMX là lỗi JavaScript. → Đã dùng thuộc tính
`form="filter-form"` của HTML5 để ô này được gửi kèm form lọc.

**4. Danh sách sản phẩm trong Admin phân trang không ổn định.**
`ProductAdmin.get_queryset()` dùng `annotate()` nên câu lệnh có `GROUP BY`, và
Django bỏ `Meta.ordering` với truy vấn gom nhóm (Django cảnh báo
`UnorderedObjectListWarning`). → Đã khai báo `ordering` tường minh.

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

## Giai đoạn 2 — E2E Test bằng Playwright

### Cài đặt bổ sung

```bash
pip install -r requirements-dev.txt
playwright install chromium        # tải trình duyệt (~150MB, chỉ cần chạy một lần)
```

### Chạy

```bash
pytest -m e2e                      # chế độ Headless (không hiện cửa sổ)
pytest -m e2e --headed             # chế độ Headed - xem trình duyệt thao tác thật
pytest -m e2e --headed --slowmo 500   # chậm lại 500ms mỗi thao tác để quan sát
pytest -m e2e --browser firefox    # đổi trình duyệt (chromium/firefox/webkit)
pytest -m e2e -k "huy_don"         # chạy riêng kịch bản huỷ đơn
```

> 💡 Chế độ `--headed --slowmo 500` rất hợp để **quay video demo đồ án**.

### Máy không có Internet?

Giao diện tải TailwindCSS, HTMX và phông chữ từ CDN. Khi chạy test, phông chữ và
CSS **luôn bị chặn** (test dùng selector ngữ nghĩa nên không cần đến CSS), còn HTMX
vẫn được tải để kịch bản đi đúng luồng thật.

Nếu máy hoặc máy chủ CI không có Internet, bật chế độ chặn toàn bộ:

```bash
E2E_OFFLINE=1 pytest -m e2e
```

Khi đó giao diện chạy ở **chế độ dự phòng**: các form giỏ hàng gửi theo cách thông
thường thay vì qua HTMX. Mọi kịch bản vẫn phải chạy đúng — đây cũng chính là cách
bộ test kiểm chứng rằng website không sập khi HTMX tải lỗi.

### Danh sách tệp

| Tệp | Nội dung |
|---|---|
| `tests/e2e/conftest.py` | Fixture live server, dữ liệu mẫu, tự chụp ảnh khi gãy |
| `tests/e2e/pages/base_page.py` | Lớp cơ sở cho mọi Page Object |
| `tests/e2e/pages/auth_pages.py` | Trang đăng ký, đăng nhập |
| `tests/e2e/pages/product_pages.py` | Danh sách và chi tiết sản phẩm |
| `tests/e2e/pages/cart_pages.py` | Giỏ hàng, thanh toán, đặt hàng thành công |
| `tests/e2e/pages/order_pages.py` | Lịch sử đơn, chi tiết đơn, huỷ đơn |
| `tests/e2e/pages/admin_pages.py` | Đăng nhập admin, lô hàng, đơn hàng, dashboard |
| `tests/e2e/test_customer_flow.py` | Kịch bản luồng khách hàng |
| `tests/e2e/test_admin_flow.py` | Kịch bản luồng quản trị viên |

Ngoài ra Giai đoạn 2 bổ sung thêm kiểm thử tích hợp (qua HTTP, không cần trình duyệt):

| Tệp | Nội dung |
|---|---|
| `tests/integration/test_auth_views.py` | Đăng ký, đăng nhập, phiên làm việc, địa chỉ |
| `tests/integration/test_catalog_views.py` | Lọc sản phẩm, HTMX partial, CRUD đánh giá |
| `tests/integration/test_cart_views.py` | Giỏ hàng, mã giảm giá, đặt hàng, huỷ đơn |
| `tests/integration/test_dashboard.py` | Dashboard admin và bảo vệ lỗi GROUP BY của SQL Server |
| `tests/integration/test_templates.py` | Template không lộ mã nguồn ra trang web |

### Mô hình Page Object Model (POM)

Mọi selector đều nằm trong lớp Page Object, **không rải rác trong test**. Khi giao
diện đổi, chỉ cần sửa một chỗ duy nhất thay vì đi sửa từng test.

```python
# Test đọc như một kịch bản, không thấy selector nào
def test_huy_don_hop_le_va_hoan_kho(self, ...):
    success = self._dat_hang(...)
    detail = OrderDetailPage(page, site_url, code=success.order_code()).go()
    assert detail.can_cancel() is True
    detail.cancel_order("Đổi ý không mua nữa")
    detail.expect_cancelled()
```

### Kịch bản đã bao phủ

**Luồng khách hàng** (`test_customer_flow.py`)
- Đăng ký tài khoản mới → tự động đăng nhập
- Đăng nhập bằng tên đăng nhập và bằng email, báo lỗi khi sai mật khẩu
- Tìm kiếm, lọc theo danh mục / thương hiệu / khoảng giá / còn hàng (qua HTMX)
- Thêm vào giỏ, tăng giảm số lượng, xoá khỏi giỏ
- Áp dụng mã giảm giá, báo lỗi khi mã không tồn tại
- **Đặt hàng → kiểm tra tồn kho giảm đúng lô (FIFO)**
- Xem lịch sử đơn hàng và lịch sử trạng thái
- **Huỷ đơn hợp lệ → kiểm tra kho hoàn về đúng lô ban đầu**
- Không cho huỷ đơn đang giao
- Viết, sửa, xoá đánh giá sản phẩm

**Luồng quản trị viên** (`test_admin_flow.py`)
- Đăng nhập `/admin`, chặn sai mật khẩu, chặn khách hàng thường
- **Thêm lô hàng mới → tồn kho tăng, có ghi vết giao dịch nhập kho**
- **Duyệt trạng thái đơn: Chờ xác nhận → Đã xác nhận → Đang giao → Hoàn thành**
- Admin huỷ đơn → kho hoàn về đúng lô
- **Dashboard: 4 thẻ thống kê khớp database, đếm đơn theo trạng thái,
  cảnh báo lô sắp hết hạn và sản phẩm sắp hết tồn kho**
- Phân quyền read-only hiển thị đúng trên giao diện (không có nút Thêm)

### Yêu cầu kỹ thuật đã đáp ứng

| Yêu cầu | Cách thực hiện |
|---|---|
| Page Object Model | 7 lớp Page Object trong `tests/e2e/pages/` |
| Auto-waiting | Dùng `expect()` và `wait_for_selector` của Playwright — **không có `sleep` nào trong bộ test** |
| Chụp ảnh khi test gãy | Hook `pytest_runtest_makereport` + fixture `screenshot_on_failure`, ảnh lưu vào `tests/e2e/screenshots/` |
| Headless & Headed | Mặc định Headless; thêm cờ `--headed` để xem trình duyệt thao tác |

### Ảnh chụp khi test gãy

Khi một test E2E thất bại, ảnh màn hình được lưu tự động:

```
📸 Đã lưu ảnh màn hình lúc test gãy: tests/e2e/screenshots/test_huy_don_hop_le.png
```

Thư mục `tests/e2e/screenshots/` đã nằm trong `.gitignore`.

### Vài lưu ý kỹ thuật

**Vì sao E2E phải dùng `django_db(transaction=True)`?**
`live_server` dựng web server ở một luồng khác. Dữ liệu nằm trong transaction chưa
commit sẽ không được luồng đó nhìn thấy, nên fixture phải commit thật.

**Vì sao cần `DJANGO_ALLOW_ASYNC_UNSAFE`?**
API đồng bộ của Playwright chạy bên trong một event loop. Django phát hiện có event
loop thì chặn mọi truy vấn đồng bộ. Cờ này (đặt trong `tests/e2e/conftest.py`) cho
phép fixture tạo dữ liệu bình thường.

**Biến `PLAYWRIGHT_CHROMIUM_PATH`**
Trỏ tới một bản Chromium đã cài sẵn trên máy chủ CI, thay vì bắt Playwright tải bản
riêng. Không đặt thì Playwright dùng trình duyệt do `playwright install` tải về.

---

## Vướng mắc cần quyết định

### ✅ Đã chốt: Giai đoạn 3 dùng phương án A (xây REST API)

Sẽ cài `djangorestframework` + `djangorestframework-simplejwt`, viết Serializer và
ViewSet cho Auth / Products / Orders / Warehouse, rồi mới làm Postman Collection.

<details>
<summary>Bối cảnh của quyết định này</summary>

### Giai đoạn 3 (Postman) chưa thực hiện được với code hiện tại

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

</details>

### ✅ Đã xử lý: hợp nhất về một bộ test duy nhất

Bộ cũ kiểu `django.test.TestCase` ở `apps/*/tests.py` (62 test) **đã được xoá**.
Toàn bộ coverage được chuyển sang `tests/`:

| Bộ cũ | Chuyển sang |
|---|---|
| `apps/accounts/tests.py` | `tests/unit/test_models.py` + `tests/integration/test_auth_views.py` |
| `apps/catalog/tests.py` | `tests/unit/test_models.py` + `tests/integration/test_catalog_views.py` |
| `apps/inventory/tests.py` | `tests/unit/test_services.py` |
| `apps/orders/tests.py` | `tests/unit/test_services.py` |
| `apps/core/tests.py` | `tests/integration/test_cart_views.py` + `test_dashboard.py` + `tests/unit/test_permissions.py` |

Giờ chỉ còn một lệnh duy nhất: `pytest`.

---

## 📚 Tài liệu bảo vệ đồ án

| Tài liệu | Nội dung |
|---|---|
| [docs/BAO-VE-DO-AN.md](docs/BAO-VE-DO-AN.md) | Kim tự tháp kiểm thử, nghiệp vụ được kiểm thử, 11 lỗi phát hiện được, câu hỏi phản biện |
| [docs/DANH-MUC-TEST-CASE.md](docs/DANH-MUC-TEST-CASE.md) | Bảng chi tiết toàn bộ 293 ca (sinh tự động từ mã nguồn) |
| [docs/CHIEN-LUOC-BAT-ELEMENT.md](docs/CHIEN-LUOC-BAT-ELEMENT.md) | Cách định vị phần tử, 3 bẫy đã gặp thật, auto-waiting, Page Object Model |

> Danh mục test case được sinh bằng script phân tích cú pháp (AST) kết hợp
> `pytest --collect-only`, nên **luôn khớp với mã nguồn thực tế**.

### File Excel danh mục test case

`docs/DANH-MUC-TEST-CASE.xlsx` — 3 sheet:

| Sheet | Nội dung |
|---|---|
| **Danh muc Test Case** | 232 dòng: tên test + ý nghĩa, dữ liệu chuẩn bị, các bước thực thi, kết quả mong đợi. Có lọc và cố định dòng tiêu đề |
| **Tong hop** | Thống kê theo tầng và theo tệp |
| **Chu giai Fixture** | Giải nghĩa toàn bộ dữ liệu mẫu |

Sinh lại khi thêm test mới:
```bash
pytest -m "" --collect-only -q | grep "::" > nodes.txt
python scripts/trich_test_case.py && python scripts/sinh_excel_test_case.py
```

---

## Giai đoạn 3 — AI phân tích log lỗi tự động

Thay cho phương án Postman ban đầu (đã huỷ vì dự án không có REST API), giai đoạn 3
xây công cụ **đọc log lỗi và sinh báo cáo phân tích tự động**.

### Cách chạy

```bash
# 1. Chạy test, xuất kết quả ra JSON
pytest -m "" --json-report --json-report-file=reports/ket-qua.json

# 2. Phân tích và sinh báo cáo
python -m tools.ai_report
```

Kết quả: `reports/bao-cao-loi.md` và `reports/bao-cao-loi.html`.

Để bật phần phân tích của AI, đặt khoá API trước khi chạy:

```powershell
# Windows PowerShell
$env:DEEPSEEK_API_KEY = "sk-..."
```

```bash
# macOS / Linux
export DEEPSEEK_API_KEY="sk-..."
```

Không có khoá thì công cụ **vẫn chạy bình thường**, chỉ thiếu phần nhận định của AI.

> 🔐 **Không bao giờ ghi khoá API vào mã nguồn hay commit lên git.** Đặt qua biến
> môi trường như trên, hoặc thêm dòng `DEEPSEEK_API_KEY=sk-...` vào tệp `.env`
> (tệp này đã nằm trong `.gitignore`). Nếu lỡ để lộ khoá, hãy thu hồi và tạo khoá mới.

### Hỗ trợ hai nhà cung cấp AI

| Nhà cung cấp | Biến môi trường | Model mặc định | Đổi model bằng |
|---|---|---|---|
| **DeepSeek** *(mặc định)* | `DEEPSEEK_API_KEY` | `deepseek-chat` | `DEEPSEEK_MODEL` |
| Claude | `ANTHROPIC_API_KEY` | `claude-opus-5` | `CLAUDE_MODEL` |

Công cụ tự phát hiện theo khoá đang có. Có cả hai thì ưu tiên DeepSeek; muốn chỉ định
rõ thì đặt `AI_PROVIDER=deepseek` hoặc `AI_PROVIDER=claude`.

**Khác biệt kỹ thuật giữa hai bên** — đây là điểm đáng nêu khi bảo vệ:

DeepSeek dùng giao thức tương thích OpenAI, có chế độ `response_format={"type":"json_object"}`
bảo đảm trả về **JSON hợp lệ**, nhưng **không bảo đảm đúng lược đồ** — AI vẫn có thể
thiếu trường hoặc điền giá trị ngoài danh sách cho phép. Vì vậy công cụ **kiểm tra lại
bằng Pydantic** sau khi nhận, và báo lỗi rõ ràng nếu sai thay vì để dữ liệu hỏng lọt vào
báo cáo. Claude thì ràng buộc lược đồ ngay ở phía máy chủ nên không cần bước này —
nhưng công cụ vẫn kiểm tra cho cả hai, vì phòng thủ nhiều lớp là rẻ.

| Tuỳ chọn | Ý nghĩa |
|---|---|
| `--input` | Tệp JSON kết quả (mặc định `reports/ket-qua.json`) |
| `--out` | Thư mục xuất báo cáo (mặc định `reports/`) |
| `--no-ai` | Chỉ gom nhóm, không gọi API |

### Cấu trúc

| Tệp | Nhiệm vụ |
|---|---|
| `tools/ai_report/redact.py` | **Lọc thông tin nhạy cảm** trước khi gửi ra ngoài |
| `tools/ai_report/collect.py` | Đọc kết quả pytest, gom nhóm lỗi, đính kèm ảnh E2E |
| `tools/ai_report/history.py` | So sánh với lần chạy trước |
| `tools/ai_report/analyze.py` | Gọi DeepSeek hoặc Claude, kiểm tra lược đồ phản hồi |
| `tools/ai_report/render.py` | Xuất báo cáo Markdown và HTML |

### Bốn quyết định thiết kế đáng nói khi bảo vệ

**1. Lọc thông tin nhạy cảm — có rào chắn hai lớp.**
Log kiểm thử có thể chứa mật khẩu SQL Server, khoá API, JWT, cookie phiên và đường dẫn
lộ tên người dùng. `redact.py` che chúng ngay khi trích xuất; trước lúc gửi, `analyze.py`
kiểm tra lại lần nữa và **dừng hẳn** nếu còn sót, thay vì cứ gửi đi.

Email của dữ liệu test (`@test.vn`, `@example.com`) được **giữ nguyên** để báo cáo dễ đọc —
chúng không phải thông tin thật.

**2. AI đưa ra GIẢ THUYẾT, không phải kết luận.**
Mỗi nhóm lỗi đều kèm trường **độ tin cậy** và **lỗi nằm ở đâu** (mã nguồn ứng dụng /
bài test / môi trường). Báo cáo **luôn hiển thị traceback gốc** ngay bên cạnh, cùng dòng
cảnh báo rằng phần phân tích có thể sai. Người đọc tự kiểm chứng được.

**3. Dùng JSON có lược đồ thay vì đọc văn xuôi.**
Kết quả trả về theo lược đồ Pydantic cố định nên phân tích được bằng code, không phải
dò chuỗi. Với DeepSeek, JSON hợp lệ được bảo đảm nhưng lược đồ thì không, nên có thêm
bước kiểm tra bằng Pydantic — nếu AI trả sai, công cụ báo lỗi rõ ràng thay vì để dữ
liệu hỏng lọt vào báo cáo.

**4. Gom nhóm bằng "vân tay" chuẩn hoá.**
Trước khi băm, các phần thay đổi giữa các lần chạy (địa chỉ bộ nhớ, dấu thời gian, mã đơn
hàng, con số) được thay bằng ký hiệu chung. Nhờ đó `assert 2 == 1` và `assert 4 == 1` được
nhận là **cùng một bản chất lỗi**, và vân tay ổn định qua các lần chạy nên so sánh lịch sử
mới có ý nghĩa.

### Kịch bản demo

```bash
# Cố tình phá logic FIFO trong apps/inventory/services.py:
#   .order_by(F("expiry_date").asc(...))  →  .desc(...)
pytest -m "" --json-report --json-report-file=reports/ket-qua.json
python -m tools.ai_report
```

Kết quả thực tế đã chạy thử: **11 ca thất bại gom thành 8 nhóm**, báo cáo chỉ rõ
*"8 lỗi MỚI xuất hiện — nhiều khả năng do thay đổi vừa rồi"*. Khôi phục code rồi chạy lại:
*"−11 ca hỏng · 8 lỗi đã hết"*.

### Công cụ này cũng được kiểm thử

`tests/unit/test_ai_report.py` — **54 ca**, phủ phần tất định: lọc thông tin nhạy cảm,
đọc kết quả, gom nhóm, so sánh lịch sử, xuất báo cáo, chọn nhà cung cấp AI, xử lý phản
hồi sai lược đồ và rào chắn bảo mật.

Phần **gọi API thật** không kiểm thử tự động vì kết quả không tất định và tốn chi phí.
Thay vào đó, client được **giả lập bằng `monkeypatch`** để kiểm chứng toàn bộ đường xử lý
phản hồi: JSON đúng lược đồ, JSON thiếu trường, và giá trị ngoài danh sách cho phép.

Đây là một điểm đáng nêu khi bảo vệ: **biết cái gì nên kiểm thử tự động, cái gì không, và
cách kiểm thử phần phụ thuộc dịch vụ bên ngoài mà không cần gọi dịch vụ đó**.
