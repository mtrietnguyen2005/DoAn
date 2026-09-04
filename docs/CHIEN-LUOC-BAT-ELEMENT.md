# 🎯 Chiến lược bắt element trong bộ test E2E

Tài liệu giải thích **cách định vị phần tử trên trang web** và lý do chọn cách đó.
Đây là phần dễ bị hỏi khi bảo vệ, vì chọn selector sai là nguyên nhân số một
khiến test E2E gãy vặt (flaky).

---

## 1. Thứ tự ưu tiên khi chọn selector

Nguyên tắc: **ưu tiên thứ gì gắn với chức năng, tránh thứ gắn với hình thức.**

| Ưu tiên | Loại selector | Ví dụ trong dự án | Vì sao |
|:--:|---|---|---|
| 1️⃣ | Thuộc tính `name` của form | `input[name='username']` | Backend **bắt buộc** phải có tên này để nhận dữ liệu. Đổi giao diện không làm mất nó. |
| 2️⃣ | `id` do lập trình viên đặt | `#filter-form`, `#product-results`, `#qty` | Là định danh có chủ đích, không phải ngẫu nhiên. |
| 3️⃣ | Thuộc tính dữ liệu riêng | `button[data-add-to-cart]` | Đặt ra để JavaScript dùng, nên rất ổn định. |
| 4️⃣ | Vai trò + văn bản | `button:has-text('Đặt hàng ngay')` | Gần với cách người dùng nhìn trang. |
| ❌ | **Lớp CSS trang trí** | ~~`.px-4.py-2.rounded-xl`~~ | Đây là lớp tiện ích của TailwindCSS, đổi màu nút là test gãy. |
| ❌ | **Vị trí tuyệt đối** | ~~`div > div:nth-child(3)`~~ | Thêm một thẻ `div` là sai hết. |

### Ví dụ thật trong dự án

```python
# ✅ TỐT — bám vào thuộc tính name mà backend bắt buộc phải có
self.page.fill("input[name='receiver_phone']", phone)

# ✅ TỐT — id có chủ đích
expect(self.page.locator("#product-results")).to_be_visible()

# ✅ TỐT — thuộc tính dữ liệu dành riêng cho JavaScript
self.page.locator("button[data-add-to-cart]:not([disabled])").first.click()

# ❌ XẤU — bám vào lớp trang trí, đổi thiết kế là gãy
self.page.click(".bg-brand-600.px-5.py-2\\.5.rounded-xl")
```

---

## 2. Ba cái bẫy đã gặp thật trong dự án

Đây là phần đắt giá nhất để trình bày: **không phải lý thuyết mà là lỗi đã thực sự xảy ra.**

### 🪤 Bẫy 1 — Selector quá chung, khớp nhầm phần tử khác

```python
# ❌ Lúc đầu viết thế này
self.page.click("button[type='submit']")
```

**Chuyện gì xảy ra:** Test đăng ký chạy xong thì trình duyệt nhảy sang trang
`/san-pham/?q=`. Vì trên **thanh header có ô tìm kiếm** cũng có nút submit, và
nó đứng **trước** form đăng ký trong HTML → Playwright bấm nhầm nút "Tìm".

```python
# ✅ Sửa: giới hạn vào form POST của trang
MAIN_FORM = "form[method='post']"
self.page.click(f"{MAIN_FORM} button[type='submit']")
```

> **Bài học:** Luôn hỏi "trên trang này còn phần tử nào khớp selector của mình không?"
> Thanh header và chân trang là nơi hay gây khớp nhầm nhất.

### 🪤 Bẫy 2 — Lớp CSS trùng nhau giữa header và nội dung

```python
# ❌ Đọc nhãn trạng thái đơn hàng
self.page.locator("span.rounded-full").first
```

**Chuyện gì xảy ra:** Badge số lượng giỏ hàng trên header **cũng** có lớp
`rounded-full` và nằm trước trong HTML → test đọc được số "2" thay vì chữ "Đã hủy".

```python
# ✅ Sửa: giới hạn trong vùng nội dung chính
self.page.locator("main span.rounded-full").first
```

### 🪤 Bẫy 3 — Nhiều ô cùng loại trên một form

```python
# ❌ Kiểm tra ô autocomplete đã chọn đúng chưa
expect(self.page.locator("span.select2-selection__rendered")).to_contain_text(sku)
```

**Chuyện gì xảy ra:** Form thêm lô hàng có **hai** ô autocomplete (Sản phẩm và
Nhà cung cấp) → selector khớp cả hai → khẳng định thất bại dù đã chọn đúng.

```python
# ✅ Sửa: trỏ đúng id của trường
expect(self.page.locator(f"#select2-id_{field}-container")).to_contain_text(sku)
```

---

## 3. Auto-waiting — vì sao không có `sleep` nào

Playwright có cơ chế **tự chờ**: trước mỗi thao tác nó kiểm tra phần tử đã
*xuất hiện → hiện hình → ổn định → nhận được tương tác* rồi mới thực hiện.

### ❌ Sai lầm đã mắc: đọc DOM ngay sau khi bấm

```python
login_page.login(username, "mat-khau-sai")
assert "không đúng" in login_page.error_message()   # ← đọc quá sớm
```

Test **fail trong 1.46 giây** — quá nhanh, dấu hiệu rõ là trang chưa kịp tải lại.
`click()` không đảm bảo chờ xong điều hướng trước khi dòng sau đọc DOM.

### ✅ Cách đúng: dùng `expect()` — tự thử lại tới khi khớp

```python
login_page.login(username, "mat-khau-sai").expect_error("không đúng")

# Bên trong Page Object:
def expect_error(self, fragment):
    expect(self.page.locator("div.bg-rose-50").first).to_contain_text(fragment)
```

`expect()` thử lại liên tục trong 5 giây. Nếu trang tải xong sau 300ms thì nó
khớp ngay ở lần thử đó — **vừa ổn định vừa không làm test chậm đi**.

| Cách viết | Vấn đề |
|---|---|
| `time.sleep(3)` | Máy nhanh thì phí 3 giây, máy chậm vẫn gãy. **Không dùng.** |
| `assert locator.inner_text() == x` | Đọc một lần, sai thời điểm là hỏng |
| `expect(locator).to_have_text(x)` | ✅ Tự thử lại, khớp là đi tiếp ngay |

> **Ngoại lệ cần tránh:** `wait_for_load_state("networkidle")`. Lúc đầu em có
> dùng, nhưng trang tải phông chữ và CSS từ CDN bên ngoài — mạng chậm là chờ vô
> tận, test bị treo tới hết giờ. Đã bỏ hoàn toàn, thay bằng chờ đúng phần tử cần dùng.

---

## 4. Page Object Model — gom selector về một chỗ

**Vấn đề nếu không dùng:** selector nằm rải rác trong hàng chục test. Đổi giao
diện một chút là phải sửa hàng chục chỗ.

**Cách làm:** mỗi trang một lớp, selector chỉ tồn tại bên trong lớp đó.

```python
# tests/e2e/pages/cart_pages.py — nơi DUY NHẤT biết về selector
class CartPage(BasePage):
    path = "/gio-hang/"

    @property
    def line_items(self):
        return self.page.locator("#cart-items > div > div")

    def increase_first_item(self):
        self.line_items.first.locator("button:has-text('+')").click()
        return self

    def expect_first_item_quantity(self, quantity: int):
        expect(self.line_items.first.locator("form span").first) \
            .to_have_text(str(quantity))
        return self
```

```python
# tests/e2e/test_customer_flow.py — test đọc như kịch bản, KHÔNG thấy selector
def test_tang_giam_so_luong_trong_gio(self, product_list_page, cart_page, shop_data):
    product_list_page.go().add_first_product_to_cart()
    cart_page.go().expect_first_item_quantity(1)
    cart_page.increase_first_item().expect_first_item_quantity(2)
    cart_page.decrease_first_item().expect_first_item_quantity(1)
```

**Lợi ích cụ thể đã dùng tới:** khi phát hiện bẫy số 2 (lớp `rounded-full` trùng
nhau), em chỉ sửa **một dòng** trong `order_pages.py`, không phải đụng vào bất kỳ
test nào.

### 7 lớp Page Object trong dự án

| Lớp | Trang phụ trách |
|---|---|
| `BasePage` | Lớp cơ sở: điều hướng, badge giỏ hàng, khẳng định URL |
| `RegisterPage`, `LoginPage` | Đăng ký, đăng nhập |
| `ProductListPage`, `ProductDetailPage` | Danh sách, chi tiết, bộ lọc, đánh giá |
| `CartPage`, `CheckoutPage`, `OrderSuccessPage` | Giỏ hàng, thanh toán |
| `OrderListPage`, `OrderDetailPage` | Lịch sử đơn, huỷ đơn |
| `AdminLoginPage`, `AdminDashboardPage` | Đăng nhập và dashboard quản trị |
| `AdminBatchPage`, `AdminOrderPage` | Quản lý lô hàng, duyệt đơn |

---

## 5. Xử lý phần tử động

### Ô autocomplete (select2) của Django Admin

Đây là loại phần tử khó nhất: giá trị nạp qua AJAX, không có sẵn trong HTML.

```python
def _select_autocomplete(self, field: str, term: str):
    # 1. Mở dropdown
    self.page.click(f"select[name='{field}'] + span.select2")
    # 2. Gõ từ khoá — phải là từ khoá THẬT SỰ khớp với search_fields
    self.page.locator("input.select2-search__field").fill(term)
    # 3. Chờ kết quả AJAX rồi chọn
    option = self.page.locator("li.select2-results__option", has_text=term).first
    expect(option).to_be_visible()
    option.click()
    # 4. Khẳng định đã gán thật — để lỗi lộ ra NGAY tại đây
    expect(self.page.locator(f"#select2-id_{field}-container")).to_contain_text(term)
```

**Bước 4 là kinh nghiệm rút ra:** nếu thiếu nó, khi chọn hụt thì test sẽ báo lỗi
mơ hồ ở bước lưu form ("hết thời gian chờ nút Lưu"), rất khó lần ra nguyên nhân.
Thêm khẳng định ngay sau thao tác giúp **lỗi nói đúng chỗ nó xảy ra**.

### Hộp thoại xác nhận (confirm)

```python
def cancel_order(self, reason):
    self.page.fill("textarea[name='reason']", reason)
    self.page.once("dialog", lambda dialog: dialog.accept())   # đăng ký TRƯỚC
    self.page.click("button:has-text('Xác nhận hủy đơn')")
```

Phải đăng ký trình xử lý **trước** khi bấm, vì hộp thoại chặn luồng ngay lập tức.

### Nút bị vô hiệu hoá

```python
# Sản phẩm hết hàng có nút disabled — bấm vào sẽ chờ tới hết giờ
self.page.locator("#product-results button[data-add-to-cart]:not([disabled])").first.click()
```

---

## 6. Chặn tài nguyên ngoài để test ổn định

Trang web tải TailwindCSS, HTMX và phông chữ từ CDN. Trong test:

```python
COSMETIC_HOSTS = ("fonts.googleapis.com", "cdn.tailwindcss.com", ...)

def handler(route):
    url = route.request.url
    if url.startswith(site_url):
        route.continue_()          # tài nguyên của chính web → cho qua
    elif offline or any(h in url for h in COSMETIC_HOSTS):
        route.abort()              # phông chữ, CSS trang trí → chặn
    else:
        route.continue_()          # HTMX → vẫn cho tải
```

**Vì sao chặn được mà test vẫn đúng?** Vì selector bám vào `name`, `id` và văn
bản — **không bám vào CSS**. Đây chính là lợi ích trực tiếp của nguyên tắc ở mục 1.

Biến `E2E_OFFLINE=1` chặn toàn bộ, dùng khi máy không có Internet. Khi đó giao
diện chạy ở chế độ dự phòng (form gửi thông thường thay vì qua HTMX) — và bộ test
**vẫn phải xanh**, qua đó kiểm chứng luôn rằng website không sập khi HTMX lỗi.

---

## 7. Tóm tắt để trả lời khi bảo vệ

> **Hỏi:** Em bắt element trong web như thế nào?
>
> **Đáp:** Em ưu tiên theo thứ tự: thuộc tính `name` của form → `id` → thuộc tính
> `data-*` → văn bản hiển thị. Em **tránh bám vào lớp CSS của Tailwind** vì đó là
> lớp trang trí, đổi thiết kế là test gãy hàng loạt.
>
> Toàn bộ selector được gom vào 7 lớp Page Object, test không chứa selector nào.
> Nhờ vậy khi em phát hiện lỗi khớp nhầm phần tử, em chỉ sửa một dòng.
>
> Em không dùng `sleep` ở bất kỳ đâu, mà dùng `expect()` của Playwright — nó tự
> thử lại tới khi điều kiện đúng, vừa ổn định vừa không làm test chậm.
>
> Em đã gặp ba lỗi khớp nhầm thật: nút submit khớp nhầm ô tìm kiếm trên header,
> lớp `rounded-full` khớp nhầm badge giỏ hàng, và một form có hai ô autocomplete.
> Cách xử lý chung là **giới hạn phạm vi selector** — theo form, theo vùng `main`,
> hoặc theo `id` của trường.
