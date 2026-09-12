# 📋 Danh mục toàn bộ Test Case

> Sinh lại tự động từ mã nguồn thật bằng `pytest --collect-only` (lấy đúng 307 node id, kể cả tổ hợp `parametrize`) ghép với docstring trích bằng phân tích cú pháp (AST). Khi test thay đổi, chạy lại quy trình này để cập nhật — không sửa tay.

**Tổng cộng: 307 ca kiểm thử** (185 Unit + 85 Integration + 37 E2E)

| Giai đoạn | Số ca |
|---|---|
| Unit | 185 |
| Integration | 85 |
| E2E (Playwright) | 37 |
| **Tổng** | **307** |

---

## GIAI ĐOẠN 1 — UNIT TEST — 185 ca

### 📄 `test_ai_report.py` — 51 ca

#### 🔹 `TestLocThongTinNhayCam` — 14 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_che_duoc_thong_tin_nhay_cam` `[DB_PASSWORD=MatKhauSieuBiMat123-MatKhauSieuBiMat123]` 🔁 | che duoc thong tin nhay cam |
| 2 | `test_che_duoc_thong_tin_nhay_cam` `[SERVER=localhost;UID=pcparts_user;PWD=Secret@99;-Secret@99]` 🔁 | che duoc thong tin nhay cam |
| 3 | `test_che_duoc_thong_tin_nhay_cam` `[api_key = 'sk-ant-api03-abcdefghijklmnopqrst'-sk-ant-api03]` 🔁 | che duoc thong tin nhay cam |
| 4 | `test_che_duoc_thong_tin_nhay_cam` `[create(password='matkhauthat')-matkhauthat]` 🔁 | che duoc thong tin nhay cam |
| 5 | `test_che_duoc_thong_tin_nhay_cam` `[token = eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.dozjgNryP4J3jVmNHl-eyJhbGci]` 🔁 | che duoc thong tin nhay cam |
| 6 | `test_che_duoc_thong_tin_nhay_cam` `[File "C:\Users\NguyenVanA\DoAn\x.py"-NguyenVanA]` 🔁 | che duoc thong tin nhay cam |
| 7 | `test_che_duoc_thong_tin_nhay_cam` `[/home/trietnguyen/DoAn/manage.py-trietnguyen]` 🔁 | che duoc thong tin nhay cam |
| 8 | `test_che_duoc_thong_tin_nhay_cam` `[sessionid=abc123def456ghi789jkl-abc123def456ghi789jkl]` 🔁 | che duoc thong tin nhay cam |
| 9 | `test_che_duoc_thong_tin_nhay_cam` `[Liên hệ: nguoithat@gmail.com-nguoithat@gmail.com]` 🔁 | che duoc thong tin nhay cam |
| 10 | `test_giu_nguyen_email_dung_trong_test` | Email của dữ liệu test không phải thông tin thật, giữ lại cho dễ đọc |
| 11 | `test_khong_con_sot_sau_khi_loc` | khong con sot sau khi loc |
| 12 | `test_loc_hai_lan_cho_ket_qua_giong_nhau` | Lọc lại chuỗi đã lọc không được làm hỏng thêm |
| 13 | `test_loc_duoc_cau_truc_long_nhau` | loc duoc cau truc long nhau |
| 14 | `test_chuoi_rong_khong_gay_loi` | chuoi rong khong gay loi |

#### 🔹 `TestDocKetQua` — 6 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_bao_loi_khi_thieu_tep` | bao loi khi thieu tep |
| 2 | `test_tom_tat_dung_so_lieu` | tom tat dung so lieu |
| 3 | `test_chi_trich_cac_ca_that_bai` | chi trich cac ca that bai |
| 4 | `test_nhan_dien_dung_tang` | nhan dien dung tang |
| 5 | `test_bo_tien_to_E_cua_pytest` | bo tien to E cua pytest |
| 6 | `test_traceback_da_duoc_loc` | Đây là điểm mấu chốt: traceback tuyệt đối không được mang mật khẩu |

#### 🔹 `TestGopNhieuTepKetQua` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_cong_don_so_lieu` | cong don so lieu |
| 2 | `test_gom_du_cac_ca_tu_moi_tep` | gom du cac ca tu moi tep |
| 3 | `test_mot_tep_thi_tra_ve_nguyen_ven` | mot tep thi tra ve nguyen ven |
| 4 | `test_thieu_mot_tep_thi_bao_loi_ro_rang` | thieu mot tep thi bao loi ro rang |

#### 🔹 `TestGomNhom` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_gop_cac_loi_cung_ban_chat` | assert 2 == 1 và assert 4 == 1 là cùng một bản chất lỗi |
| 2 | `test_khong_gop_loi_khac_ban_chat` | khong gop loi khac ban chat |
| 3 | `test_chuan_hoa_bo_phan_thay_doi` | chuan hoa bo phan thay doi |
| 4 | `test_van_tay_on_dinh` | Chạy lại cùng dữ liệu phải cho cùng vân tay, để so sánh lịch sử có nghĩa |
| 5 | `test_khong_co_loi_thi_khong_co_nhom` | khong co loi thi khong co nhom |

#### 🔹 `TestLichSu` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_lan_dau_chay_chua_co_lich_su` | lan dau chay chua co lich su |
| 2 | `test_ghi_va_doc_lai` | ghi va doc lai |
| 3 | `test_thoi_diem_luu_dang_doc_duoc` | Dấu thời gian phải là ISO đọc được, không phải số epoch của pytest |
| 4 | `test_nhan_dien_loi_moi_va_loi_da_sua` | nhan dien loi moi va loi da sua |
| 5 | `test_khong_co_lan_truoc_thi_moi_loi_deu_la_moi` | khong co lan truoc thi moi loi deu la moi |
| 6 | `test_chi_giu_so_lan_gioi_han` | chi giu so lan gioi han |
| 7 | `test_tep_lich_su_hong_khong_lam_gay_quy_trinh` | tep lich su hong khong lam gay quy trinh |

#### 🔹 `TestXuatBaoCao` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_xuat_du_hai_dinh_dang` | xuat du hai dinh dang |
| 2 | `test_bao_cao_khong_lo_thong_tin_nhay_cam` | bao cao khong lo thong tin nhay cam |
| 3 | `test_luon_kem_traceback_goc` | Người đọc phải tự kiểm chứng được, không chỉ tin lời AI |
| 4 | `test_canh_bao_ai_co_the_sai` | canh bao ai co the sai |
| 5 | `test_bao_khi_chua_bat_ai` | bao khi chua bat ai |
| 6 | `test_tat_ca_dat_thi_bao_cao_bao_thanh_cong` | tat ca dat thi bao cao bao thanh cong |
| 7 | `test_html_hop_le` | html hop le |

#### 🔹 `TestKiemTraKhoaApi` — 2 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_chua_co_khoa_thi_khong_goi_duoc` | chua co khoa thi khong goi duoc |
| 2 | `test_co_khoa_deepseek_thi_goi_duoc` | co khoa deepseek thi goi duoc |

#### 🔹 `TestXuLyPhanHoiDeepSeek` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_phan_hoi_dung_luoc_do` | phan hoi dung luoc do |
| 2 | `test_phan_hoi_sai_luoc_do_bi_tu_choi` | AI trả về JSON hợp lệ nhưng thiếu trường bắt buộc thì phải báo lỗi rõ ràng |
| 3 | `test_muc_do_ngoai_danh_sach_bi_tu_choi` | muc do ngoai danh sach bi tu choi |

#### 🔹 `TestRaoChanBaoMat` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dung_lai_neu_con_sot_thong_tin_nhay_cam` | Rào chắn cuối: phát hiện sót thì DỪNG, tuyệt đối không gửi đi |
| 2 | `test_khong_co_khoa_api_thi_tra_ve_none` | khong co khoa api thi tra ve none |
| 3 | `test_khong_co_loi_thi_khong_goi_api` | khong co loi thi khong goi api |

### 📄 `test_models.py` — 56 ca

#### 🔹 `TestProductStock` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_san_pham_chua_co_lo_thi_ton_kho_bang_0` | san pham chua co lo thi ton kho bang 0 |
| 2 | `test_ton_kho_cong_don_tu_nhieu_lo` | ton kho cong don tu nhieu lo |
| 3 | `test_ton_kho_cap_nhat_khi_lo_thay_doi` | ton kho cap nhat khi lo thay doi |
| 4 | `test_lo_het_hang_khong_con_tinh_vao_ton_kho` | lo het hang khong con tinh vao ton kho |
| 5 | `test_them_lo_moi_lam_tang_ton_kho` | them lo moi lam tang ton kho |

#### 🔹 `TestBatchModel` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_so_luong_da_ban` | so luong da ban |
| 2 | `test_tong_gia_von_cua_lo` | tong gia von cua lo |
| 3 | `test_ngay_nhap_kho_mac_dinh_la_hom_nay` | ngay nhap kho mac dinh la hom nay |
| 4 | `test_thu_tu_mac_dinh_theo_ngay_nhap_kho` | Meta.ordering xếp lô nhập trước lên đầu — nền tảng của FIFO |
| 5 | `test_khong_cho_so_luong_con_lai_lon_hon_so_luong_nhap` | khong cho so luong con lai lon hon so luong nhap |
| 6 | `test_khong_cho_ngay_san_xuat_sau_ngay_nhap_kho` | khong cho ngay san xuat sau ngay nhap kho |
| 7 | `test_ma_lo_phai_la_duy_nhat` | ma lo phai la duy nhat |

#### 🔹 `TestProductPricing` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_khong_khuyen_mai_thi_gia_ban_la_gia_goc` | khong khuyen mai thi gia ban la gia goc |
| 2 | `test_co_khuyen_mai_thi_uu_tien_gia_khuyen_mai` | co khuyen mai thi uu tien gia khuyen mai |
| 3 | `test_phan_tram_giam_lam_tron_xuong` | phan tram giam lam tron xuong |
| 4 | `test_bo_qua_gia_khuyen_mai_cao_hon_gia_goc` | bo qua gia khuyen mai cao hon gia goc |
| 5 | `test_gia_khuyen_mai_bang_gia_goc_khong_tinh_la_giam` | gia khuyen mai bang gia goc khong tinh la giam |

#### 🔹 `TestPromoCode` — 11 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_ma_giam_theo_phan_tram` | ma giam theo phan tram |
| 2 | `test_ma_giam_phan_tram_bi_chan_boi_muc_giam_toi_da` | ma giam phan tram bi chan boi muc giam toi da |
| 3 | `test_ma_giam_so_tien_co_dinh` | ma giam so tien co dinh |
| 4 | `test_so_tien_giam_khong_vuot_qua_gia_tri_don` | so tien giam khong vuot qua gia tri don |
| 5 | `test_ma_duoc_chuyen_thanh_chu_hoa` | ma duoc chuyen thanh chu hoa |
| 6 | `test_ma_hop_le_khong_bao_loi` | ma hop le khong bao loi |
| 7 | `test_bao_loi_khi_ma_het_han` | bao loi khi ma het han |
| 8 | `test_bao_loi_khi_chua_du_gia_tri_don_toi_thieu` | bao loi khi chua du gia tri don toi thieu |
| 9 | `test_bao_loi_khi_ma_bi_vo_hieu_hoa` | bao loi khi ma bi vo hieu hoa |
| 10 | `test_bao_loi_khi_het_luot_su_dung` | bao loi khi het luot su dung |
| 11 | `test_gioi_han_bang_0_nghia_la_khong_gioi_han` | gioi han bang 0 nghia la khong gioi han |

#### 🔹 `TestOrderTotals` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_tong_tien_bang_tam_tinh_cong_ship_tru_giam` | tong tien bang tam tinh cong ship tru giam |
| 2 | `test_gia_von_va_loi_nhuan_cua_tung_dong_hang` | gia von va loi nhuan cua tung dong hang |
| 3 | `test_tong_gia_von_va_loi_nhuan_cua_ca_don` | tong gia von va loi nhuan cua ca don |
| 4 | `test_ma_don_hang_duoc_sinh_tu_dong` | ma don hang duoc sinh tu dong |

#### 🔹 `TestOrderStatus` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_quyen_huy_don_theo_tung_trang_thai` `[pending-True]` 🔁 | quyen huy don theo tung trang thai |
| 2 | `test_quyen_huy_don_theo_tung_trang_thai` `[confirmed-True]` 🔁 | quyen huy don theo tung trang thai |
| 3 | `test_quyen_huy_don_theo_tung_trang_thai` `[shipping-False]` 🔁 | quyen huy don theo tung trang thai |
| 4 | `test_quyen_huy_don_theo_tung_trang_thai` `[completed-False]` 🔁 | quyen huy don theo tung trang thai |
| 5 | `test_quyen_huy_don_theo_tung_trang_thai` `[cancelled-False]` 🔁 | quyen huy don theo tung trang thai |

#### 🔹 `TestUserModel` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_mat_khau_khong_bao_gio_luu_dang_van_ban_tho` | mat khau khong bao gio luu dang van ban tho |
| 2 | `test_mat_khau_duoc_bam_bang_thuat_toan_hop_le` | mat khau duoc bam bang thuat toan hop le |
| 3 | `test_cau_hinh_production_dung_pbkdf2` | Kiểm tra settings.py không làm yếu thuật toán băm mật khẩu |
| 4 | `test_email_phai_la_duy_nhat` | email phai la duy nhat |
| 5 | `test_ten_hien_thi_uu_tien_ho_ten_day_du` | ten hien thi uu tien ho ten day du |
| 6 | `test_ten_hien_thi_lui_ve_ten_dang_nhap_khi_chua_co_ho_ten` | ten hien thi lui ve ten dang nhap khi chua co ho ten |
| 7 | `test_superuser_co_day_du_co_quyen` | superuser co day du co quyen |

#### 🔹 `TestAddressModel` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dia_chi_dau_tien_tu_dong_thanh_mac_dinh` | dia chi dau tien tu dong thanh mac dinh |
| 2 | `test_chi_ton_tai_duy_nhat_mot_dia_chi_mac_dinh` | chi ton tai duy nhat mot dia chi mac dinh |
| 3 | `test_dia_chi_cua_hai_nguoi_dung_khong_anh_huong_nhau` | dia chi cua hai nguoi dung khong anh huong nhau |
| 4 | `test_ghep_dia_chi_day_du` | ghep dia chi day du |
| 5 | `test_thuoc_tinh_dia_chi_mac_dinh_cua_user` | thuoc tinh dia chi mac dinh cua user |

#### 🔹 `TestProductMisc` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_slug_duoc_sinh_tu_dong_tu_ten` | slug duoc sinh tu dong tu ten |
| 2 | `test_slug_trung_ten_duoc_them_hau_to_so` | slug trung ten duoc them hau to so |
| 3 | `test_tach_thong_so_ky_thuat_thanh_cap_ten_gia_tri` | tach thong so ky thuat thanh cap ten gia tri |
| 4 | `test_thong_so_rong_tra_ve_danh_sach_rong` | thong so rong tra ve danh sach rong |

#### 🔹 `TestReviewModel` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_diem_danh_gia_trung_binh` | diem danh gia trung binh |
| 2 | `test_san_pham_chua_co_danh_gia` | san pham chua co danh gia |
| 3 | `test_moi_nguoi_chi_danh_gia_mot_san_pham_mot_lan` | moi nguoi chi danh gia mot san pham mot lan |

### 📄 `test_permissions.py` — 17 ca

#### 🔹 `TestReadOnlyResources` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_quyen_han_cua_admin_thuong` | quyen han cua admin thuong |
| 2 | `test_moi_truong_deu_bi_khoa_voi_admin_thuong` | moi truong deu bi khoa voi admin thuong |
| 3 | `test_ca_ba_model_deu_dung_mixin_chi_doc` `[Address]` 🔁 | Xác nhận hai model còn lại (Review, StockTransaction) dùng chung cơ chế |
| 4 | `test_ca_ba_model_deu_dung_mixin_chi_doc` `[Review]` 🔁 | Xác nhận hai model còn lại (Review, StockTransaction) dùng chung cơ chế |
| 5 | `test_ca_ba_model_deu_dung_mixin_chi_doc` `[StockTransaction]` 🔁 | Xác nhận hai model còn lại (Review, StockTransaction) dùng chung cơ chế |

#### 🔹 `TestSuperuserFullAccess` — 6 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_superuser_duoc_them_sua_xoa` `[Address]` 🔁 | superuser duoc them sua xoa |
| 2 | `test_superuser_duoc_them_sua_xoa` `[Review]` 🔁 | superuser duoc them sua xoa |
| 3 | `test_superuser_duoc_them_sua_xoa` `[StockTransaction]` 🔁 | superuser duoc them sua xoa |
| 4 | `test_superuser_khong_bi_khoa_truong` `[Address]` 🔁 | superuser khong bi khoa truong |
| 5 | `test_superuser_khong_bi_khoa_truong` `[Review]` 🔁 | superuser khong bi khoa truong |
| 6 | `test_superuser_khong_bi_khoa_truong` `[StockTransaction]` 🔁 | superuser khong bi khoa truong |

#### 🔹 `TestEditableResourcesUnaffected` — 2 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_admin_thuong_van_sua_duoc_san_pham_va_lo_hang` `[Product]` 🔁 | admin thuong van sua duoc san pham va lo hang |
| 2 | `test_admin_thuong_van_sua_duoc_san_pham_va_lo_hang` `[Batch]` 🔁 | admin thuong van sua duoc san pham va lo hang |

#### 🔹 `TestReadOnlyViaHttp` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_admin_thuong_xem_duoc_nhung_khong_them_duoc_qua_http` | admin thuong xem duoc nhung khong them duoc qua http |
| 2 | `test_admin_thuong_khong_sua_duoc_danh_gia_qua_http` | admin thuong khong sua duoc danh gia qua http |
| 3 | `test_superuser_vao_duoc_trang_them_moi_qua_http` | superuser vao duoc trang them moi qua http |
| 4 | `test_admin_thuong_van_them_duoc_san_pham` | admin thuong van them duoc san pham |

### 📄 `test_services.py` — 61 ca

#### 🔹 `TestAllocateStock` — 10 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_uu_tien_lo_nhap_kho_som_nhat` | uu tien lo nhap kho som nhat |
| 2 | `test_tru_dung_so_luong_tren_lo_duoc_chon` | tru dung so luong tren lo duoc chon |
| 3 | `test_lay_tran_sang_lo_ke_tiep_khi_lo_dau_khong_du` | lay tran sang lo ke tiep khi lo dau khong du |
| 4 | `test_hai_lo_cung_ngay_nhap_xep_theo_id` | Cùng ngày nhập thì lô tạo trước (id nhỏ hơn) được xuất trước |
| 5 | `test_bao_loi_khi_ton_kho_khong_du` | bao loi khi ton kho khong du |
| 6 | `test_khong_tru_kho_khi_xuat_that_bai` | Giao dịch phải nguyên tử: thất bại thì tồn kho giữ nguyên |
| 7 | `test_bao_loi_khi_so_luong_khong_duong` `[0]` 🔁 | bao loi khi so luong khong duong |
| 8 | `test_bao_loi_khi_so_luong_khong_duong` `[-1]` 🔁 | bao loi khi so luong khong duong |
| 9 | `test_bao_loi_khi_so_luong_khong_duong` `[-100]` 🔁 | bao loi khi so luong khong duong |
| 10 | `test_lay_toan_bo_ton_kho_con_lai` | lay toan bo ton kho con lai |

#### 🔹 `TestStockTransactionLog` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_ghi_vet_giao_dich_xuat_kho` | ghi vet giao dich xuat kho |
| 2 | `test_moi_lo_sinh_mot_ban_ghi_giao_dich_rieng` | moi lo sinh mot ban ghi giao dich rieng |
| 3 | `test_ghi_nhan_nguoi_thuc_hien` | ghi nhan nguoi thuc hien |
| 4 | `test_ghi_vet_nhap_kho` | ghi vet nhap kho |

#### 🔹 `TestReturnAndAdjustStock` — 6 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_hoan_tra_ve_dung_lo_ban_dau` | hoan tra ve dung lo ban dau |
| 2 | `test_ghi_vet_giao_dich_hoan_tra` | ghi vet giao dich hoan tra |
| 3 | `test_hoan_tra_so_luong_bang_khong_khong_lam_gi` | hoan tra so luong bang khong khong lam gi |
| 4 | `test_dieu_chinh_giam_ton_kho` | dieu chinh giam ton kho |
| 5 | `test_dieu_chinh_tang_vuot_so_luong_nhap_thi_noi_rong_so_luong_nhap` | dieu chinh tang vuot so luong nhap thi noi rong so luong nhap |
| 6 | `test_dieu_chinh_khong_doi_thi_khong_ghi_giao_dich` | dieu chinh khong doi thi khong ghi giao dich |

#### 🔹 `TestShippingFee` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_don_nho_phai_tra_phi_ship` | don nho phai tra phi ship |
| 2 | `test_don_dat_nguong_duoc_mien_phi_ship` | don dat nguong duoc mien phi ship |
| 3 | `test_don_vuot_nguong_duoc_mien_phi_ship` | don vuot nguong duoc mien phi ship |
| 4 | `test_ngay_duoi_nguong_van_phai_tra_phi` | ngay duoi nguong van phai tra phi |

#### 🔹 `TestOrderCOGS` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_luu_gia_von_cua_lo_duoc_xuat` | luu gia von cua lo duoc xuat |
| 2 | `test_gia_von_la_binh_quan_gia_quyen_khi_lay_tu_nhieu_lo` | gia von la binh quan gia quyen khi lay tu nhieu lo |
| 3 | `test_gia_von_khong_doi_khi_lo_moi_co_gia_khac` | gia von khong doi khi lo moi co gia khac |
| 4 | `test_luu_ban_sao_ten_va_ma_san_pham` | luu ban sao ten va ma san pham |
| 5 | `test_ghi_nhan_phan_bo_tung_lo` | ghi nhan phan bo tung lo |

#### 🔹 `TestOrderTotalCalculation` — 6 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_don_nho_cong_them_phi_ship` | don nho cong them phi ship |
| 2 | `test_don_lon_duoc_mien_phi_ship` | don lon duoc mien phi ship |
| 3 | `test_ap_dung_ma_giam_theo_phan_tram` | ap dung ma giam theo phan tram |
| 4 | `test_ma_giam_gia_tang_bo_dem_luot_su_dung` | ma giam gia tang bo dem luot su dung |
| 5 | `test_dat_hang_bang_gia_khuyen_mai_cua_san_pham` | dat hang bang gia khuyen mai cua san pham |
| 6 | `test_don_nhieu_dong_hang_cong_don_dung` | don nhieu dong hang cong don dung |

#### 🔹 `TestCreateOrder` — 8 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_tru_kho_khi_dat_hang` | tru kho khi dat hang |
| 2 | `test_ghi_lich_su_trang_thai_ban_dau` | ghi lich su trang thai ban dau |
| 3 | `test_don_moi_o_trang_thai_cho_xac_nhan` | don moi o trang thai cho xac nhan |
| 4 | `test_tu_dong_tao_ban_ghi_van_chuyen` | tu dong tao ban ghi van chuyen |
| 5 | `test_xoa_gio_hang_sau_khi_dat_thanh_cong` | xoa gio hang sau khi dat thanh cong |
| 6 | `test_bao_loi_khi_gio_hang_rong` | bao loi khi gio hang rong |
| 7 | `test_khong_tao_don_khi_khong_du_ton_kho` | khong tao don khi khong du ton kho |
| 8 | `test_luu_thong_tin_nguoi_nhan` | luu thong tin nguoi nhan |

#### 🔹 `TestChangeOrderStatus` — 8 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_ghi_lich_su_moi_lan_doi_trang_thai` | ghi lich su moi lan doi trang thai |
| 2 | `test_danh_dau_moc_thoi_gian_hoan_thanh` | danh dau moc thoi gian hoan thanh |
| 3 | `test_danh_dau_moc_thoi_gian_ban_giao_van_chuyen` | danh dau moc thoi gian ban giao van chuyen |
| 4 | `test_doi_sang_chinh_trang_thai_hien_tai_khong_ghi_lich_su` | doi sang chinh trang thai hien tai khong ghi lich su |
| 5 | `test_khong_cho_doi_trang_thai_don_da_huy` | khong cho doi trang thai don da huy |
| 6 | `test_khong_cho_doi_trang_thai_don_da_hoan_thanh` | khong cho doi trang thai don da hoan thanh |
| 7 | `test_van_cho_phep_huy_don_da_hoan_thanh` | Quản trị viên vẫn có thể huỷ đơn đã hoàn thành (ví dụ khách trả hàng) |
| 8 | `test_bao_loi_voi_trang_thai_khong_ton_tai` | bao loi voi trang thai khong ton tai |

#### 🔹 `TestCancelOrderRestoresStock` — 10 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_huy_don_hoan_lai_dung_tung_lo` | huy don hoan lai dung tung lo |
| 2 | `test_huy_don_ghi_vet_giao_dich_hoan_kho` | huy don ghi vet giao dich hoan kho |
| 3 | `test_danh_dau_da_hoan_de_khong_hoan_hai_lan` | danh dau da hoan de khong hoan hai lan |
| 4 | `test_goi_hoan_kho_lan_hai_khong_lam_tang_ton_kho` | goi hoan kho lan hai khong lam tang ton kho |
| 5 | `test_huy_don_hoan_lai_luot_dung_ma_giam_gia` | huy don hoan lai luot dung ma giam gia |
| 6 | `test_khong_cho_huy_don_dang_giao` | khong cho huy don dang giao |
| 7 | `test_ton_kho_khong_doi_khi_huy_don_that_bai` | ton kho khong doi khi huy don that bai |
| 8 | `test_khong_the_huy_don_hai_lan` | khong the huy don hai lan |
| 9 | `test_huy_don_ghi_lai_ly_do` | huy don ghi lai ly do |
| 10 | `test_danh_dau_moc_thoi_gian_huy` | danh dau moc thoi gian huy |


## GIAI ĐOẠN 1b — INTEGRATION TEST — 85 ca

### 📄 `test_auth_views.py` — 14 ca

#### 🔹 `TestDangKy` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dang_ky_tao_tai_khoan_va_dang_nhap_luon` | dang ky tao tai khoan va dang nhap luon |
| 2 | `test_tu_choi_email_da_ton_tai` | tu choi email da ton tai |
| 3 | `test_tu_choi_mat_khau_khong_khop` | tu choi mat khau khong khop |

#### 🔹 `TestDangNhapVaPhien` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dang_nhap_bang_ten_dang_nhap` | dang nhap bang ten dang nhap |
| 2 | `test_dang_nhap_bang_email` | dang nhap bang email |
| 3 | `test_sai_mat_khau_thi_khong_vao_duoc` | sai mat khau thi khong vao duoc |
| 4 | `test_khong_ghi_nho_thi_phien_het_khi_dong_trinh_duyet` | khong ghi nho thi phien het khi dong trinh duyet |
| 5 | `test_ghi_nho_dang_nhap_thi_giu_phien` | ghi nho dang nhap thi giu phien |
| 6 | `test_dang_xuat_bat_buoc_dung_phuong_thuc_post` | dang xuat bat buoc dung phuong thuc post |
| 7 | `test_trang_ho_so_yeu_cau_dang_nhap` | trang ho so yeu cau dang nhap |

#### 🔹 `TestDiaChiQuaHttp` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_them_dia_chi` | them dia chi |
| 2 | `test_dat_lam_dia_chi_mac_dinh` | dat lam dia chi mac dinh |
| 3 | `test_xoa_dia_chi` | xoa dia chi |
| 4 | `test_khong_dung_duoc_dia_chi_cua_nguoi_khac` | khong dung duoc dia chi cua nguoi khac |

### 📄 `test_cart_views.py` — 20 ca

#### 🔹 `TestGioHang` — 8 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_them_vao_gio` | them vao gio |
| 2 | `test_gio_hang_dung_gia_khuyen_mai` | gio hang dung gia khuyen mai |
| 3 | `test_so_luong_bi_chan_boi_ton_kho` | so luong bi chan boi ton kho |
| 4 | `test_cap_nhat_va_xoa_khoi_gio` | cap nhat va xoa khoi gio |
| 5 | `test_xoa_toan_bo_gio_hang` | xoa toan bo gio hang |
| 6 | `test_dong_bo_gio_hang_tu_localstorage` | dong bo gio hang tu localstorage |
| 7 | `test_gio_hang_duoc_giu_sau_khi_dang_nhap` | Khách vãng lai thêm hàng, đăng nhập xong giỏ vẫn còn nguyên |
| 8 | `test_khong_them_duoc_san_pham_het_hang` | khong them duoc san pham het hang |

#### 🔹 `TestMaGiamGiaQuaHttp` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_ap_dung_ma_hop_le` | ap dung ma hop le |
| 2 | `test_go_ma_giam_gia` | go ma giam gia |
| 3 | `test_ma_het_han_bi_tu_choi` | ma het han bi tu choi |

#### 🔹 `TestDatHangQuaHttp` — 6 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_thanh_toan_yeu_cau_dang_nhap` | thanh toan yeu cau dang nhap |
| 2 | `test_gio_rong_thi_khong_vao_duoc_trang_thanh_toan` | gio rong thi khong vao duoc trang thanh toan |
| 3 | `test_dat_hang_thanh_cong_qua_http` | dat hang thanh cong qua http |
| 4 | `test_so_dien_thoai_khong_hop_le_bi_tu_choi` | so dien thoai khong hop le bi tu choi |
| 5 | `test_huy_don_qua_http` | huy don qua http |
| 6 | `test_khong_xem_duoc_don_cua_nguoi_khac` | khong xem duoc don cua nguoi khac |

#### 🔹 `TestCsrfChoKhachVangLai` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_trang_cong_luon_phat_hanh_csrf_token` | Mọi trang đều phải có thẻ meta csrf-token và đặt cookie csrftoken |
| 2 | `test_khach_vang_lai_them_duoc_vao_gio_khi_bat_kiem_tra_csrf` | khach vang lai them duoc vao gio khi bat kiem tra csrf |
| 3 | `test_thieu_token_thi_bi_chan` | Đối chứng: không có token thì server phải từ chối |

### 📄 `test_catalog_views.py` — 22 ca

#### 🔹 `TestLocSanPham` — 8 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_tim_theo_tu_khoa` | tim theo tu khoa |
| 2 | `test_loc_theo_thuong_hieu` | loc theo thuong hieu |
| 3 | `test_loc_theo_gia_toi_thieu` | loc theo gia toi thieu |
| 4 | `test_loc_theo_gia_toi_da` | loc theo gia toi da |
| 5 | `test_chi_hien_san_pham_con_hang` | chi hien san pham con hang |
| 6 | `test_chi_hien_san_pham_dang_giam_gia` | chi hien san pham dang giam gia |
| 7 | `test_sap_xep_theo_gia_tang_dan` | sap xep theo gia tang dan |
| 8 | `test_yeu_cau_htmx_chi_tra_ve_luoi_san_pham` | Lọc bằng HTMX chỉ nạp lại phần lưới, không nạp lại cả trang |

#### 🔹 `TestDanhGiaQuaHttp` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_chua_dang_nhap_thi_khong_gui_duoc_danh_gia` | chua dang nhap thi khong gui duoc danh gia |
| 2 | `test_tao_sua_xoa_danh_gia` | tao sua xoa danh gia |
| 3 | `test_moi_nguoi_chi_danh_gia_mot_lan` | moi nguoi chi danh gia mot lan |
| 4 | `test_khong_sua_duoc_danh_gia_cua_nguoi_khac` | khong sua duoc danh gia cua nguoi khac |

#### 🔹 `TestCacTrangCong` — 10 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_trang_cong_mo_duoc` `[core:home]` 🔁 | trang cong mo duoc |
| 2 | `test_trang_cong_mo_duoc` `[core:about]` 🔁 | trang cong mo duoc |
| 3 | `test_trang_cong_mo_duoc` `[core:contact]` 🔁 | trang cong mo duoc |
| 4 | `test_trang_cong_mo_duoc` `[catalog:product_list]` 🔁 | trang cong mo duoc |
| 5 | `test_trang_cong_mo_duoc` `[catalog:brand_list]` 🔁 | trang cong mo duoc |
| 6 | `test_trang_cong_mo_duoc` `[catalog:supplier_list]` 🔁 | trang cong mo duoc |
| 7 | `test_trang_cong_mo_duoc` `[content:news_list]` 🔁 | trang cong mo duoc |
| 8 | `test_trang_cong_mo_duoc` `[content:promotion_list]` 🔁 | trang cong mo duoc |
| 9 | `test_trang_chi_tiet_san_pham` | trang chi tiet san pham |
| 10 | `test_luot_xem_tang_sau_moi_lan_xem` | luot xem tang sau moi lan xem |

### 📄 `test_dashboard.py` — 12 ca

#### 🔹 `TestDashboard` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_tra_ve_du_cac_muc_thong_ke` | tra ve du cac muc thong ke |
| 2 | `test_dem_don_hang_theo_trang_thai` | dem don hang theo trang thai |
| 3 | `test_liet_ke_san_pham_sap_het_ton_kho` | liet ke san pham sap het ton kho |
| 4 | `test_moi_cot_trong_order_by_deu_phai_co_trong_group_by` | Chặn tái phát lỗi 8127 của SQL Server |
| 5 | `test_truy_van_gom_nhom_khong_mang_theo_ordering_mac_dinh` | truy van gom nhom khong mang theo ordering mac dinh |

#### 🔹 `TestTrangAdminMoDuoc` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_superuser_mo_duoc_moi_trang` `[/admin/]` 🔁 | superuser mo duoc moi trang |
| 2 | `test_superuser_mo_duoc_moi_trang` `[/admin/accounts/address/]` 🔁 | superuser mo duoc moi trang |
| 3 | `test_superuser_mo_duoc_moi_trang` `[/admin/catalog/product/]` 🔁 | superuser mo duoc moi trang |
| 4 | `test_superuser_mo_duoc_moi_trang` `[/admin/inventory/stocktransaction/]` 🔁 | superuser mo duoc moi trang |
| 5 | `test_superuser_mo_duoc_moi_trang` `[/admin/orders/order/]` 🔁 | superuser mo duoc moi trang |
| 6 | `test_superuser_mo_duoc_moi_trang` `[/admin/content/banner/]` 🔁 | superuser mo duoc moi trang |
| 7 | `test_trang_sua_don_hang` | trang sua don hang |

### 📄 `test_templates.py` — 17 ca

#### 🔹 `TestGhiChuTemplate` — 1 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_khong_co_ghi_chu_mot_dau_trai_nhieu_dong` | khong co ghi chu mot dau trai nhieu dong |

#### 🔹 `TestTrangKhongLoMaNguon` — 16 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_trang_cong` `[core:home]` 🔁 | trang cong |
| 2 | `test_trang_cong` `[core:about]` 🔁 | trang cong |
| 3 | `test_trang_cong` `[core:contact]` 🔁 | trang cong |
| 4 | `test_trang_cong` `[catalog:product_list]` 🔁 | trang cong |
| 5 | `test_trang_cong` `[catalog:brand_list]` 🔁 | trang cong |
| 6 | `test_trang_cong` `[catalog:supplier_list]` 🔁 | trang cong |
| 7 | `test_trang_cong` `[content:news_list]` 🔁 | trang cong |
| 8 | `test_trang_cong` `[content:promotion_list]` 🔁 | trang cong |
| 9 | `test_trang_cong` `[orders:cart_detail]` 🔁 | trang cong |
| 10 | `test_trang_cong` `[accounts:login]` 🔁 | trang cong |
| 11 | `test_trang_cong` `[accounts:register]` 🔁 | trang cong |
| 12 | `test_trang_chi_tiet_san_pham` | trang chi tiet san pham |
| 13 | `test_trang_gio_hang_co_san_pham` | trang gio hang co san pham |
| 14 | `test_trang_thanh_toan` | trang thanh toan |
| 15 | `test_trang_don_hang` | trang don hang |
| 16 | `test_trang_tai_khoan` | trang tai khoan |


## GIAI ĐOẠN 2 — E2E TEST — 37 ca

### 📄 `test_admin_flow.py` — 14 ca

#### 🔹 `TestDangNhapAdmin` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dang_nhap_admin_thanh_cong` `[chromium]` 🔁 | dang nhap admin thanh cong |
| 2 | `test_sai_mat_khau_khong_vao_duoc` `[chromium]` 🔁 | sai mat khau khong vao duoc |
| 3 | `test_khach_hang_thuong_khong_vao_duoc_admin` `[chromium]` 🔁 | Tài khoản không phải staff bị giữ lại ở trang đăng nhập |

#### 🔹 `TestQuanLyLoHang` — 2 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_them_lo_hang_moi_va_ghi_vet_nhap_kho` `[chromium]` 🔁 | them lo hang moi va ghi vet nhap kho |
| 2 | `test_lo_hang_moi_hien_trong_danh_sach` `[chromium]` 🔁 | lo hang moi hien trong danh sach |

#### 🔹 `TestDuyetTrangThaiDonHang` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_doi_trang_thai_don_va_ghi_lich_su` `[chromium]` 🔁 | doi trang thai don va ghi lich su |
| 2 | `test_duyet_qua_nhieu_trang_thai_den_hoan_thanh` `[chromium]` 🔁 | duyet qua nhieu trang thai den hoan thanh |
| 3 | `test_admin_huy_don_thi_kho_duoc_hoan_dung_lo` `[chromium]` 🔁 | admin huy don thi kho duoc hoan dung lo |

#### 🔹 `TestDashboardThongKe` — 2 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dashboard_hien_du_bon_the_thong_ke` `[chromium]` 🔁 | dashboard hien du bon the thong ke |
| 2 | `test_dashboard_mo_duoc_tren_sql_server` `[chromium]` 🔁 | Chặn tái phát lỗi 8127 (ORDER BY không nằm trong GROUP BY) |

#### 🔹 `TestPhanQuyenReadOnlyTrenGiaoDien` — 4 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_khong_co_nut_them_moi` `[chromium-/admin/accounts/address/]` 🔁 | khong co nut them moi |
| 2 | `test_khong_co_nut_them_moi` `[chromium-/admin/catalog/review/]` 🔁 | khong co nut them moi |
| 3 | `test_khong_co_nut_them_moi` `[chromium-/admin/inventory/stocktransaction/]` 🔁 | khong co nut them moi |
| 4 | `test_van_them_duoc_san_pham` `[chromium]` 🔁 | van them duoc san pham |

### 📄 `test_customer_flow.py` — 23 ca

#### 🔹 `TestDangKyVaDangNhap` — 5 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dang_ky_tai_khoan_moi_thanh_cong` `[chromium]` 🔁 | dang ky tai khoan moi thanh cong |
| 2 | `test_dang_ky_that_bai_khi_email_da_ton_tai` `[chromium]` 🔁 | dang ky that bai khi email da ton tai |
| 3 | `test_dang_nhap_bang_ten_dang_nhap` `[chromium]` 🔁 | dang nhap bang ten dang nhap |
| 4 | `test_dang_nhap_bang_email` `[chromium]` 🔁 | dang nhap bang email |
| 5 | `test_dang_nhap_sai_mat_khau_bao_loi` `[chromium]` 🔁 | dang nhap sai mat khau bao loi |

#### 🔹 `TestTimKiemVaLocSanPham` — 3 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_hien_thi_toan_bo_san_pham` `[chromium]` 🔁 | hien thi toan bo san pham |
| 2 | `test_tim_kiem_theo_tu_khoa` `[chromium]` 🔁 | tim kiem theo tu khoa |
| 3 | `test_khong_tim_thay_thi_hien_thong_bao` `[chromium]` 🔁 | khong tim thay thi hien thong bao |

#### 🔹 `TestGioHang` — 6 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_them_san_pham_vao_gio_tu_trang_danh_sach` `[chromium]` 🔁 | them san pham vao gio tu trang danh sach |
| 2 | `test_them_san_pham_voi_so_luong_tuy_chon` `[chromium]` 🔁 | them san pham voi so luong tuy chon |
| 3 | `test_tang_giam_so_luong_trong_gio` `[chromium]` 🔁 | tang giam so luong trong gio |
| 4 | `test_xoa_san_pham_khoi_gio` `[chromium]` 🔁 | xoa san pham khoi gio |
| 5 | `test_ap_dung_ma_giam_gia` `[chromium]` 🔁 | ap dung ma giam gia |
| 6 | `test_ma_giam_gia_khong_ton_tai_bao_loi` `[chromium]` 🔁 | ma giam gia khong ton tai bao loi |

#### 🔹 `TestDatHangVaHuyDon` — 7 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_dat_hang_thanh_cong` `[chromium]` 🔁 | dat hang thanh cong |
| 2 | `test_dat_hang_lam_giam_ton_kho_dung_lo` `[chromium]` 🔁 | Lô nhập kho sớm phải bị trừ trước (FIFO) |
| 3 | `test_gio_hang_duoc_xoa_sau_khi_dat` `[chromium]` 🔁 | gio hang duoc xoa sau khi dat |
| 4 | `test_xem_lich_su_don_hang` `[chromium]` 🔁 | xem lich su don hang |
| 5 | `test_xem_chi_tiet_don_va_lich_su_trang_thai` `[chromium]` 🔁 | xem chi tiet don va lich su trang thai |
| 6 | `test_huy_don_hop_le_va_hoan_kho` `[chromium]` 🔁 | Huỷ đơn ở trạng thái Chờ xác nhận: được phép, và kho phải hoàn đúng lô |
| 7 | `test_khong_cho_huy_don_dang_giao` `[chromium]` 🔁 | khong cho huy don dang giao |

#### 🔹 `TestDanhGiaSanPham` — 2 ca

| # | Test case | Mô tả |
|:--:|---|---|
| 1 | `test_viet_sua_va_xoa_danh_gia` `[chromium]` 🔁 | viet sua va xoa danh gia |
| 2 | `test_khach_chua_dang_nhap_khong_viet_duoc_danh_gia` `[chromium]` 🔁 | khach chua dang nhap khong viet duoc danh gia |

