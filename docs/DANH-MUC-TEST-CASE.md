# 📋 Danh mục toàn bộ Test Case

> Tài liệu **sinh tự động** từ mã nguồn bằng `scripts/sinh_md_test_case.py`: tên và
> mô tả lấy bằng phân tích cú pháp (AST), số ca lấy từ `pytest --collect-only`.
> Luôn khớp với code thực tế — sửa test rồi chạy lại script, không sửa tay tệp này.

**Tổng cộng: 313 ca kiểm thử** (190 Unit + 86 Integration + 37 E2E)

| Giai đoạn | Số ca |
|---|---|
| Unit | 190 |
| Integration | 86 |
| E2E (Playwright) | 37 |
| **Tổng** | **313** |


---

## GIAI ĐOẠN 1 — UNIT TEST — 190 ca

### 📄 `test_ai_report.py` — 55 ca

> Kiểm thử công cụ phân tích log lỗi bằng AI. Chỉ kiểm thử phần TẤT ĐỊNH (lọc thông tin nhạy cảm, gom nhóm, so sánh lịch sử, xuất báo cáo). Phần gọi API không kiểm thử ở đây vì kết quả không tất định và tốn chi phí — nó được giả lập bằng đối tượng thay thế.

#### 🔹 `TestLocThongTinNhayCam` — 14 ca

**Mục đích:** Không được để lọt mật khẩu, khoá API hay đường dẫn cá nhân ra ngoài.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_che_duoc_thong_tin_nhay_cam` 🔁<br>Che duoc thong tin nhay cam | Che duoc thong tin nhay cam |
| 2 | `test_giu_nguyen_email_dung_trong_test`<br>Giu nguyen email dung trong test | Email của dữ liệu test không phải thông tin thật, giữ lại cho dễ đọc. |
| 3 | `test_khong_con_sot_sau_khi_loc`<br>Khong con sot sau khi loc | Khong con sot sau khi loc |
| 4 | `test_loc_hai_lan_cho_ket_qua_giong_nhau`<br>Loc hai lan cho ket qua giong nhau | Lọc lại chuỗi đã lọc không được làm hỏng thêm. |
| 5 | `test_loc_duoc_cau_truc_long_nhau`<br>Loc duoc cau truc long nhau | Loc duoc cau truc long nhau |
| 6 | `test_chuoi_rong_khong_gay_loi`<br>Chuoi rong khong gay loi | Chuoi rong khong gay loi |


#### 🔹 `TestDocKetQua` — 6 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_bao_loi_khi_thieu_tep`<br>Bao loi khi thieu tep | Bao loi khi thieu tep |
| 2 | `test_tom_tat_dung_so_lieu`<br>Tom tat dung so lieu | Tom tat dung so lieu |
| 3 | `test_chi_trich_cac_ca_that_bai`<br>Chi trich cac ca that bai | Chi trich cac ca that bai |
| 4 | `test_nhan_dien_dung_tang`<br>Nhan dien dung tang | Nhan dien dung tang |
| 5 | `test_bo_tien_to_E_cua_pytest`<br>Bo tien to e cua pytest | Bo tien to e cua pytest |
| 6 | `test_traceback_da_duoc_loc`<br>Traceback da duoc loc | Đây là điểm mấu chốt: traceback tuyệt đối không được mang mật khẩu. |


#### 🔹 `TestGopNhieuTepKetQua` — 4 ca

**Mục đích:** Chạy test làm nhiều lượt (tách E2E ra riêng) rồi gộp kết quả lại.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_cong_don_so_lieu`<br>Cong don so lieu | Cong don so lieu |
| 2 | `test_gom_du_cac_ca_tu_moi_tep`<br>Gom du cac ca tu moi tep | Gom du cac ca tu moi tep |
| 3 | `test_mot_tep_thi_tra_ve_nguyen_ven`<br>Mot tep thi tra ve nguyen ven | Mot tep thi tra ve nguyen ven |
| 4 | `test_thieu_mot_tep_thi_bao_loi_ro_rang`<br>Thieu mot tep thi bao loi ro rang | Thieu mot tep thi bao loi ro rang |


#### 🔹 `TestGomNhom` — 5 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_gop_cac_loi_cung_ban_chat`<br>Gop cac loi cung ban chat | assert 2 == 1 và assert 4 == 1 là cùng một bản chất lỗi. |
| 2 | `test_khong_gop_loi_khac_ban_chat`<br>Khong gop loi khac ban chat | Khong gop loi khac ban chat |
| 3 | `test_chuan_hoa_bo_phan_thay_doi`<br>Chuan hoa bo phan thay doi | Chuan hoa bo phan thay doi |
| 4 | `test_van_tay_on_dinh`<br>Van tay on dinh | Chạy lại cùng dữ liệu phải cho cùng vân tay, để so sánh lịch sử có nghĩa. |
| 5 | `test_khong_co_loi_thi_khong_co_nhom`<br>Khong co loi thi khong co nhom | Khong co loi thi khong co nhom |


#### 🔹 `TestLichSu` — 7 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_lan_dau_chay_chua_co_lich_su`<br>Lan dau chay chua co lich su | Lan dau chay chua co lich su |
| 2 | `test_ghi_va_doc_lai`<br>Ghi va doc lai | Ghi va doc lai |
| 3 | `test_thoi_diem_luu_dang_doc_duoc`<br>Thoi diem luu dang doc duoc | Dấu thời gian phải là ISO đọc được, không phải số epoch của pytest. |
| 4 | `test_nhan_dien_loi_moi_va_loi_da_sua`<br>Nhan dien loi moi va loi da sua | Nhan dien loi moi va loi da sua |
| 5 | `test_khong_co_lan_truoc_thi_moi_loi_deu_la_moi`<br>Khong co lan truoc thi moi loi deu la moi | Khong co lan truoc thi moi loi deu la moi |
| 6 | `test_chi_giu_so_lan_gioi_han`<br>Chi giu so lan gioi han | Chi giu so lan gioi han |
| 7 | `test_tep_lich_su_hong_khong_lam_gay_quy_trinh`<br>Tep lich su hong khong lam gay quy trinh | Tep lich su hong khong lam gay quy trinh |


#### 🔹 `TestXuatBaoCao` — 7 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_xuat_du_hai_dinh_dang`<br>Xuat du hai dinh dang | Xuat du hai dinh dang |
| 2 | `test_bao_cao_khong_lo_thong_tin_nhay_cam`<br>Bao cao khong lo thong tin nhay cam | Bao cao khong lo thong tin nhay cam |
| 3 | `test_luon_kem_traceback_goc`<br>Luon kem traceback goc | Người đọc phải tự kiểm chứng được, không chỉ tin lời AI. |
| 4 | `test_canh_bao_ai_co_the_sai`<br>Canh bao ai co the sai | Canh bao ai co the sai |
| 5 | `test_bao_khi_chua_bat_ai`<br>Bao khi chua bat ai | Bao khi chua bat ai |
| 6 | `test_tat_ca_dat_thi_bao_cao_bao_thanh_cong`<br>Tat ca dat thi bao cao bao thanh cong | Tat ca dat thi bao cao bao thanh cong |
| 7 | `test_html_hop_le`<br>Html hop le | Html hop le |


#### 🔹 `TestChonNhaCungCap` — 6 ca

**Mục đích:** Công cụ hỗ trợ cả DeepSeek lẫn Claude, chọn theo khoá API đang có.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_chua_co_khoa_nao`<br>Chua co khoa nao | Chua co khoa nao |
| 2 | `test_tu_nhan_deepseek`<br>Tu nhan deepseek | Tu nhan deepseek |
| 3 | `test_tu_nhan_claude`<br>Tu nhan claude | Tu nhan claude |
| 4 | `test_co_ca_hai_thi_uu_tien_deepseek`<br>Co ca hai thi uu tien deepseek | Co ca hai thi uu tien deepseek |
| 5 | `test_bien_AI_PROVIDER_thang_tat_ca`<br>Bien ai provider thang tat ca | Bien ai provider thang tat ca |
| 6 | `test_gia_tri_AI_PROVIDER_la_bi_bo_qua`<br>Gia tri ai provider la bi bo qua | Đặt sai tên nhà cung cấp thì quay về tự phát hiện, không gãy. |


#### 🔹 `TestXuLyPhanHoiDeepSeek` — 3 ca

**Mục đích:** DeepSeek bảo đảm trả về JSON hợp lệ nhưng KHÔNG bảo đảm đúng lược đồ. Vì vậy phải kiểm tra lại bằng Pydantic. Nhóm test này giả lập phản hồi để kiểm chứng đường xử lý mà không cần gọi API thật.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_phan_hoi_dung_luoc_do`<br>Phan hoi dung luoc do | Phan hoi dung luoc do |
| 2 | `test_phan_hoi_sai_luoc_do_bi_tu_choi`<br>Phan hoi sai luoc do bi tu choi | AI trả về JSON hợp lệ nhưng thiếu trường bắt buộc thì phải báo lỗi rõ ràng. |
| 3 | `test_muc_do_ngoai_danh_sach_bi_tu_choi`<br>Muc do ngoai danh sach bi tu choi | Muc do ngoai danh sach bi tu choi |


#### 🔹 `TestRaoChanBaoMat` — 3 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dung_lai_neu_con_sot_thong_tin_nhay_cam`<br>Dung lai neu con sot thong tin nhay cam | Rào chắn cuối: phát hiện sót thì DỪNG, tuyệt đối không gửi đi. |
| 2 | `test_khong_co_khoa_api_thi_tra_ve_none`<br>Khong co khoa api thi tra ve none | Khong co khoa api thi tra ve none |
| 3 | `test_khong_co_loi_thi_khong_goi_api`<br>Khong co loi thi khong goi api | Khong co loi thi khong goi api |


### 📄 `test_models.py` — 57 ca

> GIAI ĐOẠN 1 — Unit Test tầng Model. Kiểm thử các thuộc tính tính toán và ràng buộc nghiệp vụ nằm ngay trong ``models.py``: tồn kho theo lô, giá bán, giá vốn, mã giảm giá, đơn hàng, địa chỉ và tài khoản người dùng.

#### 🔹 `TestProductStock` — 5 ca

**Mục đích:** Tồn kho của sản phẩm phải luôn bằng TỔNG số lượng còn lại của các lô.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_san_pham_chua_co_lo_thi_ton_kho_bang_0`<br>San pham chua co lo thi ton kho bang 0 | San pham chua co lo thi ton kho bang 0 |
| 2 | `test_ton_kho_cong_don_tu_nhieu_lo`<br>Ton kho cong don tu nhieu lo | Ton kho cong don tu nhieu lo |
| 3 | `test_ton_kho_cap_nhat_khi_lo_thay_doi`<br>Ton kho cap nhat khi lo thay doi | Ton kho cap nhat khi lo thay doi |
| 4 | `test_lo_het_hang_khong_con_tinh_vao_ton_kho`<br>Lo het hang khong con tinh vao ton kho | Lo het hang khong con tinh vao ton kho |
| 5 | `test_them_lo_moi_lam_tang_ton_kho`<br>Them lo moi lam tang ton kho | Them lo moi lam tang ton kho |


#### 🔹 `TestBatchModel` — 8 ca

**Mục đích:** Các thuộc tính và ràng buộc của Lô hàng.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_so_luong_da_ban`<br>So luong da ban | So luong da ban |
| 2 | `test_tong_gia_von_cua_lo`<br>Tong gia von cua lo | Tong gia von cua lo |
| 3 | `test_so_ngay_con_lai_den_han`<br>So ngay con lai den han | So ngay con lai den han |
| 4 | `test_nhan_biet_lo_da_het_han`<br>Nhan biet lo da het han | Nhan biet lo da het han |
| 5 | `test_lo_khong_co_han_su_dung`<br>Lo khong co han su dung | Lo khong co han su dung |
| 6 | `test_khong_cho_so_luong_con_lai_lon_hon_so_luong_nhap`<br>Khong cho so luong con lai lon hon so luong nhap | Khong cho so luong con lai lon hon so luong nhap |
| 7 | `test_khong_cho_han_su_dung_truoc_ngay_san_xuat`<br>Khong cho han su dung truoc ngay san xuat | Khong cho han su dung truoc ngay san xuat |
| 8 | `test_ma_lo_phai_la_duy_nhat`<br>Ma lo phai la duy nhat | Ma lo phai la duy nhat |


#### 🔹 `TestProductPricing` — 5 ca

**Mục đích:** Giá thực bán, phần trăm giảm giá và số tiền tiết kiệm.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_khong_khuyen_mai_thi_gia_ban_la_gia_goc`<br>Khong khuyen mai thi gia ban la gia goc | Khong khuyen mai thi gia ban la gia goc |
| 2 | `test_co_khuyen_mai_thi_uu_tien_gia_khuyen_mai`<br>Co khuyen mai thi uu tien gia khuyen mai | Co khuyen mai thi uu tien gia khuyen mai |
| 3 | `test_phan_tram_giam_lam_tron_xuong`<br>Phan tram giam lam tron xuong | Phan tram giam lam tron xuong |
| 4 | `test_bo_qua_gia_khuyen_mai_cao_hon_gia_goc`<br>Bo qua gia khuyen mai cao hon gia goc | Bo qua gia khuyen mai cao hon gia goc |
| 5 | `test_gia_khuyen_mai_bang_gia_goc_khong_tinh_la_giam`<br>Gia khuyen mai bang gia goc khong tinh la giam | Gia khuyen mai bang gia goc khong tinh la giam |


#### 🔹 `TestPromoCode` — 11 ca

**Mục đích:** Quy tắc tính tiền giảm và điều kiện áp dụng mã.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_ma_giam_theo_phan_tram`<br>Ma giam theo phan tram | Ma giam theo phan tram |
| 2 | `test_ma_giam_phan_tram_bi_chan_boi_muc_giam_toi_da`<br>Ma giam phan tram bi chan boi muc giam toi da | Ma giam phan tram bi chan boi muc giam toi da |
| 3 | `test_ma_giam_so_tien_co_dinh`<br>Ma giam so tien co dinh | Ma giam so tien co dinh |
| 4 | `test_so_tien_giam_khong_vuot_qua_gia_tri_don`<br>So tien giam khong vuot qua gia tri don | So tien giam khong vuot qua gia tri don |
| 5 | `test_ma_duoc_chuyen_thanh_chu_hoa`<br>Ma duoc chuyen thanh chu hoa | Ma duoc chuyen thanh chu hoa |
| 6 | `test_ma_hop_le_khong_bao_loi`<br>Ma hop le khong bao loi | Ma hop le khong bao loi |
| 7 | `test_bao_loi_khi_ma_het_han`<br>Bao loi khi ma het han | Bao loi khi ma het han |
| 8 | `test_bao_loi_khi_chua_du_gia_tri_don_toi_thieu`<br>Bao loi khi chua du gia tri don toi thieu | Bao loi khi chua du gia tri don toi thieu |
| 9 | `test_bao_loi_khi_ma_bi_vo_hieu_hoa`<br>Bao loi khi ma bi vo hieu hoa | Bao loi khi ma bi vo hieu hoa |
| 10 | `test_bao_loi_khi_het_luot_su_dung`<br>Bao loi khi het luot su dung | Bao loi khi het luot su dung |
| 11 | `test_gioi_han_bang_0_nghia_la_khong_gioi_han`<br>Gioi han bang 0 nghia la khong gioi han | Gioi han bang 0 nghia la khong gioi han |


#### 🔹 `TestOrderTotals` — 4 ca

**Mục đích:** Công thức: Tổng tiền = (Giá × Số lượng) + Phí ship − Giảm giá.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_tong_tien_bang_tam_tinh_cong_ship_tru_giam`<br>Tong tien bang tam tinh cong ship tru giam | Tong tien bang tam tinh cong ship tru giam |
| 2 | `test_gia_von_va_loi_nhuan_cua_tung_dong_hang`<br>Gia von va loi nhuan cua tung dong hang | Gia von va loi nhuan cua tung dong hang |
| 3 | `test_tong_gia_von_va_loi_nhuan_cua_ca_don`<br>Tong gia von va loi nhuan cua ca don | Tong gia von va loi nhuan cua ca don |
| 4 | `test_ma_don_hang_duoc_sinh_tu_dong`<br>Ma don hang duoc sinh tu dong | Ma don hang duoc sinh tu dong |


#### 🔹 `TestOrderStatus` — 5 ca

**Mục đích:** Quy tắc cho phép huỷ đơn theo trạng thái.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_quyen_huy_don_theo_tung_trang_thai` 🔁<br>Quyen huy don theo tung trang thai | Quyen huy don theo tung trang thai |


#### 🔹 `TestUserModel` — 7 ca

**Mục đích:** Tạo tài khoản và mã hoá mật khẩu.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_mat_khau_khong_bao_gio_luu_dang_van_ban_tho`<br>Mat khau khong bao gio luu dang van ban tho | Mat khau khong bao gio luu dang van ban tho |
| 2 | `test_mat_khau_duoc_bam_bang_thuat_toan_hop_le`<br>Mat khau duoc bam bang thuat toan hop le | Mat khau duoc bam bang thuat toan hop le |
| 3 | `test_cau_hinh_production_dung_pbkdf2`<br>Cau hinh production dung pbkdf2 | Kiểm tra settings.py không làm yếu thuật toán băm mật khẩu. Fixture ``fast_password_hashing`` đổi sang MD5 cho nhanh, nên test này khôi phục lại cấu hình mặc định của Django để kiểm tra cho đúng. |
| 4 | `test_email_phai_la_duy_nhat`<br>Email phai la duy nhat | Email phai la duy nhat |
| 5 | `test_ten_hien_thi_uu_tien_ho_ten_day_du`<br>Ten hien thi uu tien ho ten day du | Ten hien thi uu tien ho ten day du |
| 6 | `test_ten_hien_thi_lui_ve_ten_dang_nhap_khi_chua_co_ho_ten`<br>Ten hien thi lui ve ten dang nhap khi chua co ho ten | Ten hien thi lui ve ten dang nhap khi chua co ho ten |
| 7 | `test_superuser_co_day_du_co_quyen`<br>Superuser co day du co quyen | Superuser co day du co quyen |


#### 🔹 `TestAddressModel` — 5 ca

**Mục đích:** Quy tắc địa chỉ mặc định: luôn có đúng MỘT địa chỉ mặc định.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dia_chi_dau_tien_tu_dong_thanh_mac_dinh`<br>Dia chi dau tien tu dong thanh mac dinh | Dia chi dau tien tu dong thanh mac dinh |
| 2 | `test_chi_ton_tai_duy_nhat_mot_dia_chi_mac_dinh`<br>Chi ton tai duy nhat mot dia chi mac dinh | Chi ton tai duy nhat mot dia chi mac dinh |
| 3 | `test_dia_chi_cua_hai_nguoi_dung_khong_anh_huong_nhau`<br>Dia chi cua hai nguoi dung khong anh huong nhau | Dia chi cua hai nguoi dung khong anh huong nhau |
| 4 | `test_ghep_dia_chi_day_du`<br>Ghep dia chi day du | Ghep dia chi day du |
| 5 | `test_thuoc_tinh_dia_chi_mac_dinh_cua_user`<br>Thuoc tinh dia chi mac dinh cua user | Thuoc tinh dia chi mac dinh cua user |


#### 🔹 `TestProductMisc` — 4 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_slug_duoc_sinh_tu_dong_tu_ten`<br>Slug duoc sinh tu dong tu ten | Slug duoc sinh tu dong tu ten |
| 2 | `test_slug_trung_ten_duoc_them_hau_to_so`<br>Slug trung ten duoc them hau to so | Slug trung ten duoc them hau to so |
| 3 | `test_tach_thong_so_ky_thuat_thanh_cap_ten_gia_tri`<br>Tach thong so ky thuat thanh cap ten gia tri | Tach thong so ky thuat thanh cap ten gia tri |
| 4 | `test_thong_so_rong_tra_ve_danh_sach_rong`<br>Thong so rong tra ve danh sach rong | Thong so rong tra ve danh sach rong |


#### 🔹 `TestReviewModel` — 3 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_diem_danh_gia_trung_binh`<br>Diem danh gia trung binh | Diem danh gia trung binh |
| 2 | `test_san_pham_chua_co_danh_gia`<br>San pham chua co danh gia | San pham chua co danh gia |
| 3 | `test_moi_nguoi_chi_danh_gia_mot_san_pham_mot_lan`<br>Moi nguoi chi danh gia mot san pham mot lan | Moi nguoi chi danh gia mot san pham mot lan |


### 📄 `test_permissions.py` — 17 ca

> GIAI ĐOẠN 1 — Unit Test phân quyền Read-only trong trang quản trị. Yêu cầu nghiệp vụ: ba resource nhạy cảm phải ở chế độ CHỈ ĐỌC đối với Admin thường, chỉ superuser mới được thêm/sửa/xoá: * Địa chỉ người dùng (dữ liệu cá nhân của khách) * Đánh giá sản phẩm (nội dung do khách viết, admin không được sửa hộ) * Giao dịch kho (sổ nhật ký kho, sửa được thì mất tính toàn vẹn) Cả ba dùng chung một cơ chế (``ReadOnlyForStaffMixin``), nên bộ test kiểm tra ĐẦY ĐỦ hành vi trên một model đại diện (Address), sau đó chỉ xác nhận ngắn gọn rằng hai model còn lại áp dụng đúng cùng cơ chế đó — tránh lặp lại y hệt bộ kiểm tra sáu chiều trên cả ba model một cách máy móc.

#### 🔹 `TestReadOnlyResources` — 5 ca

**Mục đích:** Kiểm tra đầy đủ hành vi chỉ-đọc trên một model đại diện (Address).

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_quyen_han_cua_admin_thuong`<br>Quyen han cua admin thuong | Quyen han cua admin thuong |
| 2 | `test_moi_truong_deu_bi_khoa_voi_admin_thuong`<br>Moi truong deu bi khoa voi admin thuong | Moi truong deu bi khoa voi admin thuong |
| 3 | `test_ca_ba_model_deu_dung_mixin_chi_doc` 🔁<br>Ca ba model deu dung mixin chi doc | Xác nhận hai model còn lại (Review, StockTransaction) dùng chung cơ chế. |


#### 🔹 `TestSuperuserFullAccess` — 6 ca

**Mục đích:** Superuser giữ toàn quyền trên chính những resource đó.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_superuser_duoc_them_sua_xoa` 🔁<br>Superuser duoc them sua xoa | Superuser duoc them sua xoa |
| 2 | `test_superuser_khong_bi_khoa_truong` 🔁<br>Superuser khong bi khoa truong | Superuser khong bi khoa truong |


#### 🔹 `TestEditableResourcesUnaffected` — 2 ca

**Mục đích:** Phân quyền chỉ đọc không được làm ảnh hưởng các resource khác.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_admin_thuong_van_sua_duoc_san_pham_va_lo_hang` 🔁<br>Admin thuong van sua duoc san pham va lo hang | Admin thuong van sua duoc san pham va lo hang |


#### 🔹 `TestReadOnlyViaHttp` — 4 ca

**Mục đích:** Kiểm chứng qua HTTP thật: trang thêm mới phải trả về 403.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_admin_thuong_xem_duoc_nhung_khong_them_duoc_qua_http`<br>Admin thuong xem duoc nhung khong them duoc qua http | Admin thuong xem duoc nhung khong them duoc qua http |
| 2 | `test_admin_thuong_khong_sua_duoc_danh_gia_qua_http`<br>Admin thuong khong sua duoc danh gia qua http | Admin thuong khong sua duoc danh gia qua http |
| 3 | `test_superuser_vao_duoc_trang_them_moi_qua_http`<br>Superuser vao duoc trang them moi qua http | Superuser vao duoc trang them moi qua http |
| 4 | `test_admin_thuong_van_them_duoc_san_pham`<br>Admin thuong van them duoc san pham | Admin thuong van them duoc san pham |


### 📄 `test_services.py` — 61 ca

> GIAI ĐOẠN 1 — Unit Test tầng Service (nghiệp vụ cốt lõi). Kiểm thử ``apps/inventory/services.py`` và ``apps/orders/services.py``: * Xuất kho theo FIFO, ưu tiên lô có hạn sử dụng sớm nhất * Ghi vết mọi giao dịch kho (nhập / xuất / hoàn trả / điều chỉnh) * Lưu giá vốn (COGS) bình quân gia quyền tại thời điểm bán * Tính tổng tiền: Giá × Số lượng + Phí ship − Giảm giá * Đổi trạng thái đơn và hoàn trả tồn kho về ĐÚNG lô ban đầu khi huỷ đơn

#### 🔹 `TestAllocateStock` — 10 ca

**Mục đích:** ``allocate_stock`` phải lấy hàng từ lô hết hạn sớm nhất trước.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_uu_tien_lo_co_han_su_dung_som_nhat`<br>Uu tien lo co han su dung som nhat | Uu tien lo co han su dung som nhat |
| 2 | `test_tru_dung_so_luong_tren_lo_duoc_chon`<br>Tru dung so luong tren lo duoc chon | Tru dung so luong tren lo duoc chon |
| 3 | `test_lay_tran_sang_lo_ke_tiep_khi_lo_dau_khong_du`<br>Lay tran sang lo ke tiep khi lo dau khong du | Lay tran sang lo ke tiep khi lo dau khong du |
| 4 | `test_lo_khong_co_han_su_dung_duoc_xuat_sau_cung`<br>Lo khong co han su dung duoc xuat sau cung | Lo khong co han su dung duoc xuat sau cung |
| 5 | `test_bao_loi_khi_ton_kho_khong_du`<br>Bao loi khi ton kho khong du | Bao loi khi ton kho khong du |
| 6 | `test_khong_tru_kho_khi_xuat_that_bai`<br>Khong tru kho khi xuat that bai | Giao dịch phải nguyên tử: thất bại thì tồn kho giữ nguyên. |
| 7 | `test_bao_loi_khi_so_luong_khong_duong` 🔁<br>Bao loi khi so luong khong duong | Bao loi khi so luong khong duong |
| 8 | `test_lay_toan_bo_ton_kho_con_lai`<br>Lay toan bo ton kho con lai | Lay toan bo ton kho con lai |


#### 🔹 `TestStockTransactionLog` — 4 ca

**Mục đích:** Mọi biến động kho đều phải để lại dấu vết truy xuất được.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_ghi_vet_giao_dich_xuat_kho`<br>Ghi vet giao dich xuat kho | Ghi vet giao dich xuat kho |
| 2 | `test_moi_lo_sinh_mot_ban_ghi_giao_dich_rieng`<br>Moi lo sinh mot ban ghi giao dich rieng | Moi lo sinh mot ban ghi giao dich rieng |
| 3 | `test_ghi_nhan_nguoi_thuc_hien`<br>Ghi nhan nguoi thuc hien | Ghi nhan nguoi thuc hien |
| 4 | `test_ghi_vet_nhap_kho`<br>Ghi vet nhap kho | Ghi vet nhap kho |


#### 🔹 `TestReturnAndAdjustStock` — 6 ca

**Mục đích:** Hoàn trả và điều chỉnh thủ công.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_hoan_tra_ve_dung_lo_ban_dau`<br>Hoan tra ve dung lo ban dau | Hoan tra ve dung lo ban dau |
| 2 | `test_ghi_vet_giao_dich_hoan_tra`<br>Ghi vet giao dich hoan tra | Ghi vet giao dich hoan tra |
| 3 | `test_hoan_tra_so_luong_bang_khong_khong_lam_gi`<br>Hoan tra so luong bang khong khong lam gi | Hoan tra so luong bang khong khong lam gi |
| 4 | `test_dieu_chinh_giam_ton_kho`<br>Dieu chinh giam ton kho | Dieu chinh giam ton kho |
| 5 | `test_dieu_chinh_tang_vuot_so_luong_nhap_thi_noi_rong_so_luong_nhap`<br>Dieu chinh tang vuot so luong nhap thi noi rong so luong nhap | Dieu chinh tang vuot so luong nhap thi noi rong so luong nhap |
| 6 | `test_dieu_chinh_khong_doi_thi_khong_ghi_giao_dich`<br>Dieu chinh khong doi thi khong ghi giao dich | Dieu chinh khong doi thi khong ghi giao dich |


#### 🔹 `TestShippingFee` — 4 ca

**Mục đích:** Miễn phí vận chuyển khi đơn đạt ngưỡng cấu hình.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_don_nho_phai_tra_phi_ship`<br>Don nho phai tra phi ship | Don nho phai tra phi ship |
| 2 | `test_don_dat_nguong_duoc_mien_phi_ship`<br>Don dat nguong duoc mien phi ship | Don dat nguong duoc mien phi ship |
| 3 | `test_don_vuot_nguong_duoc_mien_phi_ship`<br>Don vuot nguong duoc mien phi ship | Don vuot nguong duoc mien phi ship |
| 4 | `test_ngay_duoi_nguong_van_phai_tra_phi`<br>Ngay duoi nguong van phai tra phi | Ngay duoi nguong van phai tra phi |


#### 🔹 `TestOrderCOGS` — 5 ca

**Mục đích:** Giá vốn phải được chụp lại tại thời điểm bán, không phụ thuộc giá nhập sau này.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_luu_gia_von_cua_lo_duoc_xuat`<br>Luu gia von cua lo duoc xuat | Luu gia von cua lo duoc xuat |
| 2 | `test_gia_von_la_binh_quan_gia_quyen_khi_lay_tu_nhieu_lo`<br>Gia von la binh quan gia quyen khi lay tu nhieu lo | Gia von la binh quan gia quyen khi lay tu nhieu lo |
| 3 | `test_gia_von_khong_doi_khi_lo_moi_co_gia_khac`<br>Gia von khong doi khi lo moi co gia khac | Gia von khong doi khi lo moi co gia khac |
| 4 | `test_luu_ban_sao_ten_va_ma_san_pham`<br>Luu ban sao ten va ma san pham | Luu ban sao ten va ma san pham |
| 5 | `test_ghi_nhan_phan_bo_tung_lo`<br>Ghi nhan phan bo tung lo | Ghi nhan phan bo tung lo |


#### 🔹 `TestOrderTotalCalculation` — 6 ca

**Mục đích:** Công thức tổng tiền: (Giá × Số lượng) + Phí ship − Giảm giá.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_don_nho_cong_them_phi_ship`<br>Don nho cong them phi ship | Don nho cong them phi ship |
| 2 | `test_don_lon_duoc_mien_phi_ship`<br>Don lon duoc mien phi ship | Don lon duoc mien phi ship |
| 3 | `test_ap_dung_ma_giam_theo_phan_tram`<br>Ap dung ma giam theo phan tram | Ap dung ma giam theo phan tram |
| 4 | `test_ma_giam_gia_tang_bo_dem_luot_su_dung`<br>Ma giam gia tang bo dem luot su dung | Ma giam gia tang bo dem luot su dung |
| 5 | `test_dat_hang_bang_gia_khuyen_mai_cua_san_pham`<br>Dat hang bang gia khuyen mai cua san pham | Dat hang bang gia khuyen mai cua san pham |
| 6 | `test_don_nhieu_dong_hang_cong_don_dung`<br>Don nhieu dong hang cong don dung | Don nhieu dong hang cong don dung |


#### 🔹 `TestCreateOrder` — 8 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_tru_kho_khi_dat_hang`<br>Tru kho khi dat hang | Tru kho khi dat hang |
| 2 | `test_ghi_lich_su_trang_thai_ban_dau`<br>Ghi lich su trang thai ban dau | Ghi lich su trang thai ban dau |
| 3 | `test_don_moi_o_trang_thai_cho_xac_nhan`<br>Don moi o trang thai cho xac nhan | Don moi o trang thai cho xac nhan |
| 4 | `test_tu_dong_tao_ban_ghi_van_chuyen`<br>Tu dong tao ban ghi van chuyen | Tu dong tao ban ghi van chuyen |
| 5 | `test_xoa_gio_hang_sau_khi_dat_thanh_cong`<br>Xoa gio hang sau khi dat thanh cong | Xoa gio hang sau khi dat thanh cong |
| 6 | `test_bao_loi_khi_gio_hang_rong`<br>Bao loi khi gio hang rong | Bao loi khi gio hang rong |
| 7 | `test_khong_tao_don_khi_khong_du_ton_kho`<br>Khong tao don khi khong du ton kho | Khong tao don khi khong du ton kho |
| 8 | `test_luu_thong_tin_nguoi_nhan`<br>Luu thong tin nguoi nhan | Luu thong tin nguoi nhan |


#### 🔹 `TestChangeOrderStatus` — 8 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_ghi_lich_su_moi_lan_doi_trang_thai`<br>Ghi lich su moi lan doi trang thai | Ghi lich su moi lan doi trang thai |
| 2 | `test_danh_dau_moc_thoi_gian_hoan_thanh`<br>Danh dau moc thoi gian hoan thanh | Danh dau moc thoi gian hoan thanh |
| 3 | `test_danh_dau_moc_thoi_gian_ban_giao_van_chuyen`<br>Danh dau moc thoi gian ban giao van chuyen | Danh dau moc thoi gian ban giao van chuyen |
| 4 | `test_doi_sang_chinh_trang_thai_hien_tai_khong_ghi_lich_su`<br>Doi sang chinh trang thai hien tai khong ghi lich su | Doi sang chinh trang thai hien tai khong ghi lich su |
| 5 | `test_khong_cho_doi_trang_thai_don_da_huy`<br>Khong cho doi trang thai don da huy | Khong cho doi trang thai don da huy |
| 6 | `test_khong_cho_doi_trang_thai_don_da_hoan_thanh`<br>Khong cho doi trang thai don da hoan thanh | Khong cho doi trang thai don da hoan thanh |
| 7 | `test_van_cho_phep_huy_don_da_hoan_thanh`<br>Van cho phep huy don da hoan thanh | Quản trị viên vẫn có thể huỷ đơn đã hoàn thành (ví dụ khách trả hàng). |
| 8 | `test_bao_loi_voi_trang_thai_khong_ton_tai`<br>Bao loi voi trang thai khong ton tai | Bao loi voi trang thai khong ton tai |


#### 🔹 `TestCancelOrderRestoresStock` — 10 ca

**Mục đích:** Yêu cầu cốt lõi: huỷ đơn phải hoàn hàng về ĐÚNG lô đã xuất.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_huy_don_hoan_lai_dung_tung_lo`<br>Huy don hoan lai dung tung lo | Huy don hoan lai dung tung lo |
| 2 | `test_huy_don_ghi_vet_giao_dich_hoan_kho`<br>Huy don ghi vet giao dich hoan kho | Huy don ghi vet giao dich hoan kho |
| 3 | `test_danh_dau_da_hoan_de_khong_hoan_hai_lan`<br>Danh dau da hoan de khong hoan hai lan | Danh dau da hoan de khong hoan hai lan |
| 4 | `test_goi_hoan_kho_lan_hai_khong_lam_tang_ton_kho`<br>Goi hoan kho lan hai khong lam tang ton kho | Goi hoan kho lan hai khong lam tang ton kho |
| 5 | `test_huy_don_hoan_lai_luot_dung_ma_giam_gia`<br>Huy don hoan lai luot dung ma giam gia | Huy don hoan lai luot dung ma giam gia |
| 6 | `test_khong_cho_huy_don_dang_giao`<br>Khong cho huy don dang giao | Khong cho huy don dang giao |
| 7 | `test_ton_kho_khong_doi_khi_huy_don_that_bai`<br>Ton kho khong doi khi huy don that bai | Ton kho khong doi khi huy don that bai |
| 8 | `test_khong_the_huy_don_hai_lan`<br>Khong the huy don hai lan | Khong the huy don hai lan |
| 9 | `test_huy_don_ghi_lai_ly_do`<br>Huy don ghi lai ly do | Huy don ghi lai ly do |
| 10 | `test_danh_dau_moc_thoi_gian_huy`<br>Danh dau moc thoi gian huy | Danh dau moc thoi gian huy |


---

## GIAI ĐOẠN 1b — INTEGRATION TEST — 86 ca

### 📄 `test_auth_views.py` — 14 ca

> Kiểm thử tích hợp: luồng xác thực qua HTTP (không cần trình duyệt).

#### 🔹 `TestDangKy` — 3 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dang_ky_tao_tai_khoan_va_dang_nhap_luon`<br>Dang ky tao tai khoan va dang nhap luon | Dang ky tao tai khoan va dang nhap luon |
| 2 | `test_tu_choi_email_da_ton_tai`<br>Tu choi email da ton tai | Tu choi email da ton tai |
| 3 | `test_tu_choi_mat_khau_khong_khop`<br>Tu choi mat khau khong khop | Tu choi mat khau khong khop |


#### 🔹 `TestDangNhapVaPhien` — 7 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dang_nhap_bang_ten_dang_nhap`<br>Dang nhap bang ten dang nhap | Dang nhap bang ten dang nhap |
| 2 | `test_dang_nhap_bang_email`<br>Dang nhap bang email | Dang nhap bang email |
| 3 | `test_sai_mat_khau_thi_khong_vao_duoc`<br>Sai mat khau thi khong vao duoc | Sai mat khau thi khong vao duoc |
| 4 | `test_khong_ghi_nho_thi_phien_het_khi_dong_trinh_duyet`<br>Khong ghi nho thi phien het khi dong trinh duyet | Khong ghi nho thi phien het khi dong trinh duyet |
| 5 | `test_ghi_nho_dang_nhap_thi_giu_phien`<br>Ghi nho dang nhap thi giu phien | Ghi nho dang nhap thi giu phien |
| 6 | `test_dang_xuat_bat_buoc_dung_phuong_thuc_post`<br>Dang xuat bat buoc dung phuong thuc post | Dang xuat bat buoc dung phuong thuc post |
| 7 | `test_trang_ho_so_yeu_cau_dang_nhap`<br>Trang ho so yeu cau dang nhap | Trang ho so yeu cau dang nhap |


#### 🔹 `TestDiaChiQuaHttp` — 4 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_them_dia_chi`<br>Them dia chi | Them dia chi |
| 2 | `test_dat_lam_dia_chi_mac_dinh`<br>Dat lam dia chi mac dinh | Dat lam dia chi mac dinh |
| 3 | `test_xoa_dia_chi`<br>Xoa dia chi | Xoa dia chi |
| 4 | `test_khong_dung_duoc_dia_chi_cua_nguoi_khac`<br>Khong dung duoc dia chi cua nguoi khac | Khong dung duoc dia chi cua nguoi khac |


### 📄 `test_cart_views.py` — 20 ca

> Kiểm thử tích hợp: giỏ hàng qua HTTP (session + LocalStorage).

#### 🔹 `TestGioHang` — 8 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_them_vao_gio`<br>Them vao gio | Them vao gio |
| 2 | `test_gio_hang_dung_gia_khuyen_mai`<br>Gio hang dung gia khuyen mai | Gio hang dung gia khuyen mai |
| 3 | `test_so_luong_bi_chan_boi_ton_kho`<br>So luong bi chan boi ton kho | So luong bi chan boi ton kho |
| 4 | `test_cap_nhat_va_xoa_khoi_gio`<br>Cap nhat va xoa khoi gio | Cap nhat va xoa khoi gio |
| 5 | `test_xoa_toan_bo_gio_hang`<br>Xoa toan bo gio hang | Xoa toan bo gio hang |
| 6 | `test_dong_bo_gio_hang_tu_localstorage`<br>Dong bo gio hang tu localstorage | Dong bo gio hang tu localstorage |
| 7 | `test_gio_hang_duoc_giu_sau_khi_dang_nhap`<br>Gio hang duoc giu sau khi dang nhap | Khách vãng lai thêm hàng, đăng nhập xong giỏ vẫn còn nguyên. |
| 8 | `test_khong_them_duoc_san_pham_het_hang`<br>Khong them duoc san pham het hang | Khong them duoc san pham het hang |


#### 🔹 `TestMaGiamGiaQuaHttp` — 3 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_ap_dung_ma_hop_le`<br>Ap dung ma hop le | Ap dung ma hop le |
| 2 | `test_go_ma_giam_gia`<br>Go ma giam gia | Go ma giam gia |
| 3 | `test_ma_het_han_bi_tu_choi`<br>Ma het han bi tu choi | Ma het han bi tu choi |


#### 🔹 `TestDatHangQuaHttp` — 6 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_thanh_toan_yeu_cau_dang_nhap`<br>Thanh toan yeu cau dang nhap | Thanh toan yeu cau dang nhap |
| 2 | `test_gio_rong_thi_khong_vao_duoc_trang_thanh_toan`<br>Gio rong thi khong vao duoc trang thanh toan | Gio rong thi khong vao duoc trang thanh toan |
| 3 | `test_dat_hang_thanh_cong_qua_http`<br>Dat hang thanh cong qua http | Dat hang thanh cong qua http |
| 4 | `test_so_dien_thoai_khong_hop_le_bi_tu_choi`<br>So dien thoai khong hop le bi tu choi | So dien thoai khong hop le bi tu choi |
| 5 | `test_huy_don_qua_http`<br>Huy don qua http | Huy don qua http |
| 6 | `test_khong_xem_duoc_don_cua_nguoi_khac`<br>Khong xem duoc don cua nguoi khac | Khong xem duoc don cua nguoi khac |


#### 🔹 `TestCsrfChoKhachVangLai` — 3 ca

**Mục đích:** Khách chưa đăng nhập phải thêm được hàng vào giỏ. ``django.test.Client`` mặc định TẮT kiểm tra CSRF, nên các test khác trong tệp này không phát hiện được khi trang thiếu token. Nhóm test dưới đây bật ``enforce_csrf_checks=True`` để mô phỏng đúng hành vi của trình duyệt thật. Bối cảnh: trang danh sách sản phẩm và trang chủ không có form POST nào dành cho khách vãng lai, nên nếu ``base.html`` không phát hành token thì nút "Thêm vào giỏ" (gọi ``fetch``) sẽ bị chặn với lỗi 403.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_trang_cong_luon_phat_hanh_csrf_token`<br>Trang cong luon phat hanh csrf token | Mọi trang đều phải có thẻ meta csrf-token và đặt cookie csrftoken. |
| 2 | `test_khach_vang_lai_them_duoc_vao_gio_khi_bat_kiem_tra_csrf`<br>Khach vang lai them duoc vao gio khi bat kiem tra csrf | Khach vang lai them duoc vao gio khi bat kiem tra csrf |
| 3 | `test_thieu_token_thi_bi_chan`<br>Thieu token thi bi chan | Đối chứng: không có token thì server phải từ chối. |


### 📄 `test_catalog_views.py` — 22 ca

> Kiểm thử tích hợp: lọc sản phẩm và CRUD đánh giá qua HTTP.

#### 🔹 `TestLocSanPham` — 8 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_tim_theo_tu_khoa`<br>Tim theo tu khoa | Tim theo tu khoa |
| 2 | `test_loc_theo_thuong_hieu`<br>Loc theo thuong hieu | Loc theo thuong hieu |
| 3 | `test_loc_theo_gia_toi_thieu`<br>Loc theo gia toi thieu | Loc theo gia toi thieu |
| 4 | `test_loc_theo_gia_toi_da`<br>Loc theo gia toi da | Loc theo gia toi da |
| 5 | `test_chi_hien_san_pham_con_hang`<br>Chi hien san pham con hang | Chi hien san pham con hang |
| 6 | `test_chi_hien_san_pham_dang_giam_gia`<br>Chi hien san pham dang giam gia | Chi hien san pham dang giam gia |
| 7 | `test_sap_xep_theo_gia_tang_dan`<br>Sap xep theo gia tang dan | Sap xep theo gia tang dan |
| 8 | `test_yeu_cau_htmx_chi_tra_ve_luoi_san_pham`<br>Yeu cau htmx chi tra ve luoi san pham | Lọc bằng HTMX chỉ nạp lại phần lưới, không nạp lại cả trang. |


#### 🔹 `TestDanhGiaQuaHttp` — 4 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_chua_dang_nhap_thi_khong_gui_duoc_danh_gia`<br>Chua dang nhap thi khong gui duoc danh gia | Chua dang nhap thi khong gui duoc danh gia |
| 2 | `test_tao_sua_xoa_danh_gia`<br>Tao sua xoa danh gia | Tao sua xoa danh gia |
| 3 | `test_moi_nguoi_chi_danh_gia_mot_lan`<br>Moi nguoi chi danh gia mot lan | Moi nguoi chi danh gia mot lan |
| 4 | `test_khong_sua_duoc_danh_gia_cua_nguoi_khac`<br>Khong sua duoc danh gia cua nguoi khac | Khong sua duoc danh gia cua nguoi khac |


#### 🔹 `TestCacTrangCong` — 10 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_trang_cong_mo_duoc` 🔁<br>Trang cong mo duoc | Trang cong mo duoc |
| 2 | `test_trang_chi_tiet_san_pham`<br>Trang chi tiet san pham | Trang chi tiet san pham |
| 3 | `test_luot_xem_tang_sau_moi_lan_xem`<br>Luot xem tang sau moi lan xem | Luot xem tang sau moi lan xem |


### 📄 `test_dashboard.py` — 13 ca

> Kiểm thử tích hợp: trang Dashboard của Admin. Bảo vệ khỏi lỗi ORDER BY / GROUP BY của SQL Server (mã 8127). SQL Server từ chối câu lệnh có ``ORDER BY`` trên cột không nằm trong ``GROUP BY``, trong khi SQLite bỏ qua. Driver ``mssql-django`` lại giữ nguyên ``ORDER BY`` mặc định của model khi câu lệnh có ``GROUP BY``, nên mọi truy vấn gom nhóm đều phải gọi ``.order_by()``. Test này phân tích trực tiếp câu SQL sinh ra nên bắt được lỗi ngay cả khi đang chạy trên SQLite.

#### 🔹 `TestDashboard` — 6 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_tra_ve_du_cac_muc_thong_ke`<br>Tra ve du cac muc thong ke | Tra ve du cac muc thong ke |
| 2 | `test_dem_don_hang_theo_trang_thai`<br>Dem don hang theo trang thai | Dem don hang theo trang thai |
| 3 | `test_liet_ke_lo_sap_het_han`<br>Liet ke lo sap het han | Liet ke lo sap het han |
| 4 | `test_liet_ke_san_pham_sap_het_ton_kho`<br>Liet ke san pham sap het ton kho | Liet ke san pham sap het ton kho |
| 5 | `test_moi_cot_trong_order_by_deu_phai_co_trong_group_by`<br>Moi cot trong order by deu phai co trong group by | Chặn tái phát lỗi 8127 của SQL Server. |
| 6 | `test_truy_van_gom_nhom_khong_mang_theo_ordering_mac_dinh`<br>Truy van gom nhom khong mang theo ordering mac dinh | Truy van gom nhom khong mang theo ordering mac dinh |


#### 🔹 `TestTrangAdminMoDuoc` — 7 ca

**Mục đích:** Mỗi app đăng ký ít nhất một trang admin — chọn một trang đại diện cho mỗi app thay vì liệt kê hết mọi model, vì cả 16 model đều đi qua cùng một cơ chế đăng ký/render của django-unfold.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_superuser_mo_duoc_moi_trang` 🔁<br>Superuser mo duoc moi trang | Superuser mo duoc moi trang |
| 2 | `test_trang_sua_don_hang`<br>Trang sua don hang | Trang sua don hang |


### 📄 `test_templates.py` — 17 ca

> Kiểm thử chất lượng template: không để lộ mã nguồn ra trang web.

#### 🔹 `TestGhiChuTemplate` — 1 ca

**Mục đích:** Django chỉ hỗ trợ ``{# ... #}`` trên MỘT dòng. Ghi chú trải nhiều dòng sẽ không được coi là ghi chú mà in thẳng ra trang web dưới dạng văn bản. Ghi chú nhiều dòng phải dùng ``{% comment %} ... {% endcomment %}``.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_khong_co_ghi_chu_mot_dau_trai_nhieu_dong`<br>Khong co ghi chu mot dau trai nhieu dong | Khong co ghi chu mot dau trai nhieu dong |


#### 🔹 `TestTrangKhongLoMaNguon` — 16 ca

**Mục đích:** Mọi trang render ra phải sạch, không còn cú pháp template.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_trang_cong` 🔁<br>Trang cong | Trang cong |
| 2 | `test_trang_chi_tiet_san_pham`<br>Trang chi tiet san pham | Trang chi tiet san pham |
| 3 | `test_trang_gio_hang_co_san_pham`<br>Trang gio hang co san pham | Trang gio hang co san pham |
| 4 | `test_trang_thanh_toan`<br>Trang thanh toan | Trang thanh toan |
| 5 | `test_trang_don_hang`<br>Trang don hang | Trang don hang |
| 6 | `test_trang_tai_khoan`<br>Trang tai khoan | Trang tai khoan |


---

## GIAI ĐOẠN 2 — E2E TEST — 37 ca

### 📄 `test_admin_flow.py` — 14 ca

> GIAI ĐOẠN 2 — Kịch bản E2E luồng quản trị viên. Luồng: Đăng nhập /admin → Thêm lô hàng mới → Duyệt trạng thái đơn → Kiểm tra thống kê trên Dashboard.

#### 🔹 `TestDangNhapAdmin` — 3 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dang_nhap_admin_thanh_cong`<br>Dang nhap admin thanh cong | Dang nhap admin thanh cong |
| 2 | `test_sai_mat_khau_khong_vao_duoc`<br>Sai mat khau khong vao duoc | Sai mat khau khong vao duoc |
| 3 | `test_khach_hang_thuong_khong_vao_duoc_admin`<br>Khach hang thuong khong vao duoc admin | Tài khoản không phải staff bị giữ lại ở trang đăng nhập. |


#### 🔹 `TestQuanLyLoHang` — 2 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_them_lo_hang_moi_va_ghi_vet_nhap_kho`<br>Them lo hang moi va ghi vet nhap kho | Them lo hang moi va ghi vet nhap kho |
| 2 | `test_lo_hang_moi_hien_trong_danh_sach`<br>Lo hang moi hien trong danh sach | Lo hang moi hien trong danh sach |


#### 🔹 `TestDuyetTrangThaiDonHang` — 3 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_doi_trang_thai_don_va_ghi_lich_su`<br>Doi trang thai don va ghi lich su | Doi trang thai don va ghi lich su |
| 2 | `test_duyet_qua_nhieu_trang_thai_den_hoan_thanh`<br>Duyet qua nhieu trang thai den hoan thanh | Duyet qua nhieu trang thai den hoan thanh |
| 3 | `test_admin_huy_don_thi_kho_duoc_hoan_dung_lo`<br>Admin huy don thi kho duoc hoan dung lo | Admin huy don thi kho duoc hoan dung lo |


#### 🔹 `TestDashboardThongKe` — 2 ca

**Mục đích:** Độ đúng của số liệu (tổng sản phẩm, đếm theo trạng thái, cảnh báo tồn kho/hết hạn) đã được kiểm thử chi tiết ở tầng tích hợp (``tests/integration/test_dashboard.py::TestDashboard``, đọc thẳng context trả về, không qua trình duyệt). Ở tầng E2E chỉ giữ lại hai ca: xác nhận giao diện thật render đúng, và ca chặn tái phát lỗi SQL Server thật sự từng xảy ra trên chính trang này.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dashboard_hien_du_bon_the_thong_ke`<br>Dashboard hien du bon the thong ke | Dashboard hien du bon the thong ke |
| 2 | `test_dashboard_mo_duoc_tren_sql_server`<br>Dashboard mo duoc tren sql server | Chặn tái phát lỗi 8127 (ORDER BY không nằm trong GROUP BY). Trang này từng không mở được trên SQL Server. Chạy bộ test với ``TEST_ON_MSSQL=True`` sẽ kiểm chứng lại trên đúng CSDL thật. |


#### 🔹 `TestPhanQuyenReadOnlyTrenGiaoDien` — 4 ca

**Mục đích:** Admin thường chỉ xem được 3 resource nhạy cảm, không có nút Thêm.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_khong_co_nut_them_moi` 🔁<br>Khong co nut them moi | Khong co nut them moi |
| 2 | `test_van_them_duoc_san_pham`<br>Van them duoc san pham | Van them duoc san pham |


### 📄 `test_customer_flow.py` — 23 ca

> GIAI ĐOẠN 2 — Kịch bản E2E luồng khách hàng. Luồng đầy đủ: Đăng ký → Đăng nhập → Lọc sản phẩm → Thêm giỏ hàng → Đặt hàng → Xem lịch sử → Huỷ đơn hợp lệ. Toàn bộ thao tác đi qua Page Object, không có selector rải rác trong test.

#### 🔹 `TestDangKyVaDangNhap` — 5 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dang_ky_tai_khoan_moi_thanh_cong`<br>Dang ky tai khoan moi thanh cong | Dang ky tai khoan moi thanh cong |
| 2 | `test_dang_ky_that_bai_khi_email_da_ton_tai`<br>Dang ky that bai khi email da ton tai | Dang ky that bai khi email da ton tai |
| 3 | `test_dang_nhap_bang_ten_dang_nhap`<br>Dang nhap bang ten dang nhap | Dang nhap bang ten dang nhap |
| 4 | `test_dang_nhap_bang_email`<br>Dang nhap bang email | Dang nhap bang email |
| 5 | `test_dang_nhap_sai_mat_khau_bao_loi`<br>Dang nhap sai mat khau bao loi | Dang nhap sai mat khau bao loi |


#### 🔹 `TestTimKiemVaLocSanPham` — 3 ca

**Mục đích:** Logic lọc/sắp xếp đã được kiểm thử đầy đủ ở tầng tích hợp (``tests/integration/test_catalog_views.py::TestLocSanPham``, 8 ca qua HTTP trực tiếp). Ở tầng E2E chỉ cần xác nhận một lượt tìm kiếm đại diện hoạt động đúng qua giao diện thật, không lặp lại toàn bộ ma trận lọc.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_hien_thi_toan_bo_san_pham`<br>Hien thi toan bo san pham | Hien thi toan bo san pham |
| 2 | `test_tim_kiem_theo_tu_khoa`<br>Tim kiem theo tu khoa | Tim kiem theo tu khoa |
| 3 | `test_khong_tim_thay_thi_hien_thong_bao`<br>Khong tim thay thi hien thong bao | Khong tim thay thi hien thong bao |


#### 🔹 `TestGioHang` — 6 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_them_san_pham_vao_gio_tu_trang_danh_sach`<br>Them san pham vao gio tu trang danh sach | Them san pham vao gio tu trang danh sach |
| 2 | `test_them_san_pham_voi_so_luong_tuy_chon`<br>Them san pham voi so luong tuy chon | Them san pham voi so luong tuy chon |
| 3 | `test_tang_giam_so_luong_trong_gio`<br>Tang giam so luong trong gio | Tang giam so luong trong gio |
| 4 | `test_xoa_san_pham_khoi_gio`<br>Xoa san pham khoi gio | Xoa san pham khoi gio |
| 5 | `test_ap_dung_ma_giam_gia`<br>Ap dung ma giam gia | Ap dung ma giam gia |
| 6 | `test_ma_giam_gia_khong_ton_tai_bao_loi`<br>Ma giam gia khong ton tai bao loi | Ma giam gia khong ton tai bao loi |


#### 🔹 `TestDatHangVaHuyDon` — 7 ca

**Mục đích:** Kịch bản trọng tâm: đặt hàng thật rồi huỷ, kiểm tra hoàn kho.

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_dat_hang_thanh_cong`<br>Dat hang thanh cong | Dat hang thanh cong |
| 2 | `test_dat_hang_lam_giam_ton_kho_dung_lo`<br>Dat hang lam giam ton kho dung lo | Lô hết hạn sớm phải bị trừ trước (FIFO). |
| 3 | `test_gio_hang_duoc_xoa_sau_khi_dat`<br>Gio hang duoc xoa sau khi dat | Gio hang duoc xoa sau khi dat |
| 4 | `test_xem_lich_su_don_hang`<br>Xem lich su don hang | Xem lich su don hang |
| 5 | `test_xem_chi_tiet_don_va_lich_su_trang_thai`<br>Xem chi tiet don va lich su trang thai | Xem chi tiet don va lich su trang thai |
| 6 | `test_huy_don_hop_le_va_hoan_kho`<br>Huy don hop le va hoan kho | Huỷ đơn ở trạng thái Chờ xác nhận: được phép, và kho phải hoàn đúng lô. |
| 7 | `test_khong_cho_huy_don_dang_giao`<br>Khong cho huy don dang giao | Khong cho huy don dang giao |


#### 🔹 `TestDanhGiaSanPham` — 2 ca

| # | Test case | Kiểm chứng điều gì |
|:--:|---|---|
| 1 | `test_viet_sua_va_xoa_danh_gia`<br>Viet sua va xoa danh gia | Viet sua va xoa danh gia |
| 2 | `test_khach_chua_dang_nhap_khong_viet_duoc_danh_gia`<br>Khach chua dang nhap khong viet duoc danh gia | Khach chua dang nhap khong viet duoc danh gia |


---

> 🔁 = test chạy lặp với nhiều bộ dữ liệu (`@pytest.mark.parametrize`)
