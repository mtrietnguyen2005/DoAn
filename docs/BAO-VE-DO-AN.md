# 🎓 Tài liệu bảo vệ đồ án — Kiểm thử phần mềm

> Đồ án tập trung vào **kiểm thử phần mềm**. Website chỉ đóng vai trò **đối tượng
> được kiểm thử (System Under Test)**, không phải trọng tâm trình bày.

---

## 1. Tổng quan

| Chỉ số | Giá trị |
|---|---|
| Tổng số ca kiểm thử | **313** |
| Thời gian chạy toàn bộ | ~65 giây |
| Độ bao phủ mã nguồn `apps/` | **88,2%** (`orders/services.py` đạt 97,4%) |
| Số lỗi thật phát hiện được | **11** |
| Công cụ | pytest, pytest-django, Playwright |

### Mô hình Kim tự tháp kiểm thử (Test Pyramid)

```
              ▲
             ╱ ╲     E2E — 37 ca (12%)
            ╱───╲    Chậm nhất (~52s), đắt nhất, gần người dùng nhất
           ╱     ╲
          ╱───────╲  Integration — 86 ca (27%)
         ╱         ╲ Trung bình (~2s), qua HTTP thật
        ╱───────────╲
       ╱             ╲ Unit — 190 ca (61%)
      ╱───────────────╲ Nhanh nhất (~4s), rẻ nhất, nhiều nhất
```

**Vì sao chia tỉ lệ như vậy?** Càng lên cao test càng chậm, càng dễ gãy vặt và
càng khó tìm nguyên nhân khi đỏ. Nhưng càng lên cao lại càng giống người dùng thật.
Nguyên tắc: **đẩy phần lớn ca xuống tầng thấp, chỉ để lên tầng cao những luồng
nghiệp vụ quan trọng nhất.**

Điểm mấu chốt để bảo vệ: **mỗi tầng bắt được loại lỗi mà tầng khác không bắt được.**
Đồ án này có bằng chứng cụ thể cho luận điểm đó (xem mục 4).

---

## 2. Ba tầng kiểm thử — phân biệt rõ

| | Unit | Integration | E2E |
|---|---|---|---|
| **Gọi gì** | Hàm/phương thức Python | HTTP qua Django test client | Trình duyệt Chromium thật |
| **Có view?** | Không | Có | Có |
| **Có template?** | Không | Có (render HTML) | Có |
| **Có JavaScript?** | Không | **Không** | **Có** |
| **Có CSRF?** | Không | **Mặc định tắt** | **Có** |
| **Database** | SQLite tệp | SQLite tệp | SQLite tệp + server thật |
| **Tốc độ 1 ca** | ~13ms | ~20ms | ~800ms |

Hai dòng in đậm chính là **lý do phải có đủ ba tầng** — xem mục 4.

---

## 3. Nghiệp vụ được kiểm thử

### 3.1. Quản lý kho theo lô (Batch) — điểm khó nhất của đồ án

Tồn kho **không** lưu ở một cột đơn giản, mà là **tổng số lượng còn lại của tất
cả các lô**. Điều này sinh ra ba bài toán:

**a) Xuất kho theo FIFO** — khi bán hàng phải trừ từ lô nào trước?
Quy tắc: ưu tiên lô có **hạn sử dụng sớm nhất**, sau đó tới ngày nhập kho.
Lô không có hạn sử dụng xuất sau cùng.

> Dữ liệu test được thiết kế có chủ đích: lô `LO-SOM` (hạn 10 ngày, 4 sản phẩm)
> và `LO-MUON` (hạn 200 ngày, 10 sản phẩm). Đặt mua 6 sản phẩm → phải lấy **4 từ
> lô sớm + 2 từ lô muộn**, không được lấy ngược lại.

**b) Giá vốn COGS bình quân gia quyền** — hai lô có giá nhập khác nhau
(1.000.000đ và 1.200.000đ). Khi một đơn hàng lấy từ cả hai lô, giá vốn ghi vào
chi tiết đơn phải là bình quân gia quyền:

```
COGS = (4 × 1.000.000 + 2 × 1.200.000) ÷ 6 = 1.066.666đ
```

Giá vốn được **chụp lại tại thời điểm bán**. Test `test_gia_von_khong_doi_khi_lo_moi_co_gia_khac`
chứng minh: sau khi nhập lô mới giá gấp đôi, giá vốn của đơn cũ **không đổi** —
đây là yêu cầu kế toán, nếu sai thì báo cáo lợi nhuận sai toàn bộ.

**c) Hoàn kho về ĐÚNG lô ban đầu khi huỷ đơn** — không được dồn hết vào một lô.
Bảng `OrderItemBatch` ghi rõ mỗi dòng hàng lấy bao nhiêu từ lô nào, nhờ đó khi
huỷ có thể trả lại chính xác.

### 3.2. Tài chính
Công thức: `Tổng tiền = (Giá × Số lượng) + Phí ship − Giảm giá`
- Miễn phí ship khi đơn đạt ngưỡng
- Mã giảm theo % (có mức trần) và theo số tiền cố định
- Số tiền giảm không bao giờ vượt quá giá trị đơn
- Huỷ đơn phải **hoàn lại lượt dùng** mã giảm giá

### 3.3. Người dùng và phân quyền
- Mật khẩu không bao giờ lưu văn bản thô, băm bằng `pbkdf2_sha256`
- Mỗi người dùng chỉ có **đúng một** địa chỉ mặc định
- **Phân quyền chỉ đọc**: Địa chỉ, Đánh giá, Giao dịch kho — Admin thường chỉ
  xem được. Test cấp cho họ **toàn bộ permission của Django** để chứng minh thứ
  chặn họ là `ReadOnlyForStaffMixin`, không phải do thiếu quyền.

---

## 4. 🎯 Luận điểm mạnh nhất: mỗi tầng bắt lỗi mà tầng khác bỏ lọt

Đây là phần nên nhấn mạnh khi bảo vệ, vì có **bằng chứng thực nghiệm**.

### Lỗi chỉ E2E bắt được — CSRF (nghiêm trọng nhất)

**Hiện tượng:** Khách chưa đăng nhập bấm "Thêm vào giỏ" → không có gì xảy ra.

**Nguyên nhân:** Trang chủ và trang danh sách sản phẩm không có form POST nào
dành cho khách vãng lai, nên Django không phát hành CSRF token và cũng không đặt
cookie. Hàm `getCsrfToken()` trong JavaScript trả về chuỗi rỗng → POST bị chặn
**403** → **toàn bộ khách chưa đăng nhập không mua được hàng**.

**Vì sao 248 test Unit + Integration không bắt được?**
> `django.test.Client` **mặc định tắt kiểm tra CSRF** (`enforce_csrf_checks=False`).
> Test tích hợp gửi POST thành công dù trang không hề có token.
> Và JavaScript `fetch()` chỉ chạy trong trình duyệt thật.

**Bài học:** Test tích hợp mô phỏng HTTP nhưng **không mô phỏng trình duyệt**.
Sau khi phát hiện, đã bổ sung `TestCsrfChoKhachVangLai` dùng
`Client(enforce_csrf_checks=True)` để lần sau bắt được ở tầng rẻ hơn.

### Lỗi chỉ Unit bắt được — thứ tự họ tên tiếng Việt

`display_name` trả về `"An Nguyễn"` thay vì `"Nguyễn An"`, do dùng
`get_full_name()` của Django vốn ghép theo kiểu phương Tây. E2E không bắt được vì
tên nào cũng "trông giống tên".

### Lỗi chỉ chạy trên SQL Server mới lộ — `GROUP BY`

Trang Dashboard admin không mở được trên SQL Server (lỗi 8127):
`ORDER BY` trên cột không nằm trong `GROUP BY`. **SQLite bỏ qua, SQL Server từ chối.**
→ Bài học: môi trường test phải giống môi trường thật.
→ Đã bổ sung test phân tích trực tiếp câu SQL sinh ra, bắt được lỗi ngay trên SQLite.

### Bảng tổng hợp 11 lỗi phát hiện được

| # | Lỗi | Tầng phát hiện | Mức độ |
|---|---|---|---|
| 1 | Khách vãng lai không thêm được vào giỏ (CSRF) | **E2E** | 🔴 Nghiêm trọng |
| 2 | Dashboard admin sập trên SQL Server (GROUP BY) | Thủ công → Integration | 🔴 Nghiêm trọng |
| 3 | Giỏ hàng hỏng hoàn toàn khi HTMX không tải được | **E2E** | 🟠 Cao |
| 4 | Ghi chú template hiện ra trang web như văn bản | Thủ công → Integration | 🟠 Cao |
| 5 | Ô sắp xếp sản phẩm hỏng khi thiếu HTMX | **E2E** | 🟡 Trung bình |
| 6 | Thứ tự họ tên sai với tiếng Việt | **Unit** | 🟡 Trung bình |
| 7 | Danh sách sản phẩm trong Admin phân trang bấp bênh | **E2E** (cảnh báo) | 🟡 Trung bình |
| 8 | `Address.save()` để object lệch với database | **Unit** | 🟢 Thấp |
| 9 | Cấu hình Windows Authentication vô tác dụng | Thủ công | 🟡 Trung bình |
| 10 | `format_html` dùng sai mã định dạng `{:+d}` | Thủ công | 🟢 Thấp |
| 11 | Xung đột phiên bản pytest ↔ pytest-playwright | Thủ công | 🟢 Thấp |

---

## 5. Kỹ thuật kiểm thử đã áp dụng

| Kỹ thuật | Áp dụng ở đâu |
|---|---|
| **Fixture** (dữ liệu mẫu tái sử dụng) | `tests/conftest.py` — 25 fixture |
| **Factory pattern** | `product_factory`, `batch_factory`, `user_factory`, `order_factory` |
| **Parametrize** (một test, nhiều bộ dữ liệu) | Phân quyền read-only, trạng thái đơn hàng |
| **Test Double / Stub** | `StubCart` thay giỏ hàng thật khi test service |
| **Boundary testing** (kiểm thử biên) | Ngưỡng miễn phí ship: dưới ngưỡng / đúng ngưỡng / trên ngưỡng |
| **Negative testing** (ca xấu) | Mã hết hạn, tồn kho không đủ, huỷ đơn đang giao |
| **Page Object Model** | 7 lớp trong `tests/e2e/pages/` |
| **Regression test** | Mỗi lỗi tìm được đều kèm một test chặn tái phát |
| **Isolation** (cách ly) | Mỗi test chạy trong transaction riêng, rollback khi kết thúc |

### Ví dụ kiểm thử biên — ngưỡng miễn phí ship 2.000.000đ

```python
def test_don_nho_phai_tra_phi_ship(...)          # 1.999.999đ → có phí
def test_don_dat_nguong_duoc_mien_phi_ship(...)  # 2.000.000đ → miễn phí (biên)
def test_don_vuot_nguong_duoc_mien_phi_ship(...) # 2.000.001đ → miễn phí
def test_ngay_duoi_nguong_van_phai_tra_phi(...)  # sát biên dưới
```

---

## 6. Câu hỏi phản biện thường gặp

**❓ Vì sao 313 test mà chỉ mất 65 giây?**
Vì tỉ lệ kim tự tháp: 276 ca ở tầng rẻ (~6 giây), chỉ 37 ca dùng trình duyệt.
Nếu làm toàn bộ bằng E2E thì sẽ mất khoảng 4 phút — chậm gấp 6 lần.

**❓ Vì sao test chạy SQLite mà website dùng SQL Server?**
Test chạy SQLite cho nhanh và không đụng dữ liệu thật. Nhưng em có
`config/settings_test.py` với biến `TEST_ON_MSSQL=True` để chạy đúng bộ test đó
trên SQL Server. **Em đã gặp lỗi thật chỉ lộ trên SQL Server** (lỗi `GROUP BY`),
nên đây không phải lý thuyết suông.

**❓ Vì sao CSDL test là một tệp chứ không phải SQLite trong bộ nhớ?**
Ban đầu em dùng `:memory:` cho nhanh. Nhưng khi chạy chung cả bộ (`pytest --tat-ca`)
thì lần chạy **treo cứng không báo lỗi**. Em dùng `py-spy` chụp ngăn xếp tiến trình
đang treo và thấy hai luồng của web server cùng nằm trong `sqlite3.execute`. Nguyên
nhân: với SQLite bộ nhớ, Django ép mọi luồng xử lý request của `live_server` dùng
chung **một** connection (`LiveServerThread.connections_override`), nên hai request
đồng thời khoá nhau vĩnh viễn. Chuyển sang CSDL dạng tệp thì mỗi luồng có connection
riêng — 313 test chạy trọn trong ~65 giây, phần không-E2E chỉ chậm hơn 0,3 giây.

**❓ Làm sao đảm bảo các test không ảnh hưởng nhau?**
`pytest-django` chạy mỗi test trong một transaction riêng và rollback khi kết thúc.
Riêng E2E phải dùng `transaction=True` vì web server chạy ở luồng khác, dữ liệu
chưa commit thì luồng đó không nhìn thấy.

**❓ Test có phát hiện được lỗi thật không hay chỉ chạy cho có?**
11 lỗi thật, trong đó lỗi CSRF khiến **toàn bộ khách chưa đăng nhập không mua
được hàng** — và chỉ tầng E2E mới bắt được.

**❓ Vì sao không dùng Selenium?**
Playwright có **auto-waiting** sẵn: mỗi thao tác tự chờ phần tử xuất hiện, hiện
hình, ổn định rồi mới thực hiện. Toàn bộ bộ test **không có một câu `sleep` nào**.
Selenium phải tự viết `WebDriverWait` cho từng chỗ, dễ sinh test gãy vặt (flaky).

**❓ Có test nào bị flaky không?**
Có một ca lúc đầu: chọn sản phẩm trong ô autocomplete của Admin. Nguyên nhân là
em tìm bằng chuỗi `[CPU0001] Intel Core i5-13400F`, nhưng Django Admin tách từ
khoá theo dấu cách và `[CPU0001]` có ngoặc vuông nên không khớp trường `sku`.
Test pass lúc chạy riêng chỉ vì select2 còn hiển thị danh sách mặc định.
**Đã sửa bằng cách tìm theo mã SKU** và thêm khẳng định kiểm tra giá trị đã thực
sự được gán.

**❓ Độ bao phủ 88,2% — phần còn lại là gì?**
Thấp nhất là các template tag hiển thị (`core/templatetags/shop_extras.py`, 40%)
và một số nhánh xử lý tài khoản bị khoá (`accounts/backends.py`, 65,4%) — đều là
nhánh phụ, ít va chạm trong luồng chính. Em ưu tiên bao phủ **logic nghiệp vụ**
hơn chạy đua con số: `orders/services.py` — nơi chứa toàn bộ nghiệp vụ kho và
đơn hàng — đạt **97,4%**.

---

## 7. Lệnh chạy để demo

```bash
pytest                              # 276 ca Unit + Integration (~6 giây)
pytest -m e2e                       # 37 ca E2E (~52 giây)
pytest --tat-ca                     # tất cả 313 ca
pytest -m inventory                 # chỉ nhóm nghiệp vụ kho
pytest --cov=apps --cov-report=html # báo cáo độ bao phủ

pytest -m e2e --headed --slowmo 500 # ⭐ XEM TRÌNH DUYỆT TỰ THAO TÁC
TEST_ON_MSSQL=True pytest           # chạy trên SQL Server thật
```

> Lệnh có dấu ⭐ dùng để **quay video demo**: trình duyệt tự đăng ký, lọc sản phẩm,
> thêm giỏ hàng, đặt hàng rồi huỷ đơn — rất trực quan khi bảo vệ.

---

📎 Danh mục chi tiết từng ca: xem [DANH-MUC-TEST-CASE.md](DANH-MUC-TEST-CASE.md)
📎 Chiến lược bắt element: xem [CHIEN-LUOC-BAT-ELEMENT.md](CHIEN-LUOC-BAT-ELEMENT.md)
