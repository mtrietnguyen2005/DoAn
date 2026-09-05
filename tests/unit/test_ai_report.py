"""Kiểm thử công cụ phân tích log lỗi bằng AI.

Chỉ kiểm thử phần TẤT ĐỊNH (lọc thông tin nhạy cảm, gom nhóm, so sánh lịch sử,
xuất báo cáo). Phần gọi API không kiểm thử ở đây vì kết quả không tất định và
tốn chi phí — nó được giả lập bằng đối tượng thay thế.
"""
import json
from pathlib import Path

import pytest

from tools.ai_report import collect, history, redact, render

pytestmark = pytest.mark.unit


# ============================================================================
# LỌC THÔNG TIN NHẠY CẢM — phần quan trọng nhất về mặt an toàn
# ============================================================================
class TestLocThongTinNhayCam:
    """Không được để lọt mật khẩu, khoá API hay đường dẫn cá nhân ra ngoài."""

    @pytest.mark.parametrize("dau_vao,khong_duoc_chua", [
        ("DB_PASSWORD=MatKhauSieuBiMat123", "MatKhauSieuBiMat123"),
        ("SERVER=localhost;UID=pcparts_user;PWD=Secret@99;", "Secret@99"),
        ("api_key = 'sk-ant-api03-abcdefghijklmnopqrst'", "sk-ant-api03"),
        ("ANTHROPIC_API_KEY: sk-ant-xyz9876543210abcdefgh", "sk-ant-xyz"),
        (r'File "C:\Users\NguyenVanA\DoAn\x.py"', "NguyenVanA"),
        ("/home/trietnguyen/DoAn/manage.py", "trietnguyen"),
        ("create(password='matkhauthat')", "matkhauthat"),
        ("token = eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.dozjgNryP4J3jVmNHl", "eyJhbGci"),
        ("sessionid=abc123def456ghi789jkl", "abc123def456ghi789jkl"),
        ("Liên hệ: nguoithat@gmail.com", "nguoithat@gmail.com"),
    ])
    def test_che_duoc_thong_tin_nhay_cam(self, dau_vao, khong_duoc_chua):
        ket_qua = redact.loc_van_ban(dau_vao)
        assert khong_duoc_chua not in ket_qua
        assert redact.NHAN_CHE in ket_qua

    @pytest.mark.parametrize("giu_nguyen", [
        "khachhang@test.vn",
        "quantri@test.vn",
        "nguoidung@example.com",
    ])
    def test_giu_nguyen_email_dung_trong_test(self, giu_nguyen):
        """Email của dữ liệu test không phải thông tin thật, giữ lại cho dễ đọc."""
        assert giu_nguyen in redact.loc_van_ban(f"user = '{giu_nguyen}'")

    def test_khong_con_sot_sau_khi_loc(self):
        ban_do = ("DB_PASSWORD=abc123 PWD=xyz789 sk-ant-api03-qwertyuiopasdfgh "
                  r"C:\Users\PC\x.py /home/ai/y.py that@gmail.com")
        assert redact.kiem_tra_con_sot(redact.loc_van_ban(ban_do)) == []

    def test_loc_hai_lan_cho_ket_qua_giong_nhau(self):
        """Lọc lại chuỗi đã lọc không được làm hỏng thêm."""
        goc = "DB_PASSWORD=bimat và PWD=khac"
        mot_lan = redact.loc_van_ban(goc)
        assert redact.loc_van_ban(mot_lan) == mot_lan

    def test_loc_duoc_cau_truc_long_nhau(self):
        du_lieu = {"a": ["DB_PASSWORD=bimat"], "b": {"c": "sk-ant-api03-abcdefghijklmnop"}}
        ket_qua = redact.loc_du_lieu(du_lieu)
        assert "bimat" not in json.dumps(ket_qua)
        assert "sk-ant" not in json.dumps(ket_qua)

    def test_chuoi_rong_khong_gay_loi(self):
        assert redact.loc_van_ban("") == ""
        assert redact.loc_van_ban(None) == ""


# ============================================================================
# ĐỌC KẾT QUẢ VÀ GOM NHÓM
# ============================================================================
@pytest.fixture
def bao_cao_mau(tmp_path):
    """Tệp kết quả pytest giả lập, có 3 ca hỏng thuộc 2 bản chất lỗi."""
    du_lieu = {
        "created": 1700000000, "duration": 12.34,
        "summary": {"total": 100, "passed": 97, "failed": 3},
        "tests": [
            {"nodeid": "tests/unit/test_services.py::TestKho::test_fifo_a",
             "outcome": "failed", "duration": 0.02,
             "call": {"outcome": "failed",
                      "longrepr": "tests/unit/test_services.py:31: in test_fifo_a\nE   AssertionError: assert 2 == 1"}},
            {"nodeid": "tests/unit/test_services.py::TestKho::test_fifo_b",
             "outcome": "failed", "duration": 0.03,
             "call": {"outcome": "failed",
                      "longrepr": "tests/unit/test_services.py:40: in test_fifo_b\nE   AssertionError: assert 4 == 1"}},
            {"nodeid": "tests/e2e/test_customer_flow.py::TestGio::test_them",
             "outcome": "failed", "duration": 30.1,
             "call": {"outcome": "failed",
                      "longrepr": "PWD=SieuBiMat99\nE   TimeoutError: Locator.click: Timeout 30000ms exceeded."}},
            {"nodeid": "tests/unit/test_models.py::TestX::test_ok", "outcome": "passed", "duration": 0.01},
        ],
    }
    tep = tmp_path / "ket-qua.json"
    tep.write_text(json.dumps(du_lieu), encoding="utf-8")
    return tep


class TestDocKetQua:
    def test_bao_loi_khi_thieu_tep(self, tmp_path):
        with pytest.raises(FileNotFoundError) as loi:
            collect.doc_bao_cao(tmp_path / "khong-co.json")
        assert "--json-report" in str(loi.value)   # gợi ý lệnh cần chạy

    def test_tom_tat_dung_so_lieu(self, bao_cao_mau):
        tt = collect.tom_tat(collect.doc_bao_cao(bao_cao_mau))
        assert (tt["tong"], tt["dat"], tt["hong"]) == (100, 97, 3)
        assert tt["thoi_gian"] == 12.34

    def test_chi_trich_cac_ca_that_bai(self, bao_cao_mau):
        cac_ca = collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau))
        assert len(cac_ca) == 3
        assert all("test_ok" not in c.ten for c in cac_ca)

    def test_nhan_dien_dung_tang(self, bao_cao_mau):
        cac_ca = collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau))
        assert {c.tang for c in cac_ca} == {"unit", "e2e"}

    def test_bo_tien_to_E_cua_pytest(self, bao_cao_mau):
        cac_ca = collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau))
        assert all(not c.thong_diep.startswith("E ") for c in cac_ca)
        assert "AssertionError" in {c.loai_loi for c in cac_ca}

    def test_traceback_da_duoc_loc(self, bao_cao_mau):
        """Đây là điểm mấu chốt: traceback tuyệt đối không được mang mật khẩu."""
        cac_ca = collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau))
        toan_bo = " ".join(c.traceback for c in cac_ca)
        assert "SieuBiMat99" not in toan_bo
        assert redact.NHAN_CHE in toan_bo


class TestGopNhieuTepKetQua:
    """Chạy test làm nhiều lượt (tách E2E ra riêng) rồi gộp kết quả lại."""

    @pytest.fixture
    def hai_tep(self, tmp_path):
        a = tmp_path / "a.json"
        b = tmp_path / "b.json"
        a.write_text(json.dumps({
            "created": 100, "duration": 5.0,
            "summary": {"total": 10, "passed": 9, "failed": 1},
            "tests": [{"nodeid": "tests/unit/t.py::C::test_a", "outcome": "failed",
                       "call": {"outcome": "failed", "longrepr": "E   ValueError: sai"}}],
        }), encoding="utf-8")
        b.write_text(json.dumps({
            "created": 200, "duration": 30.0,
            "summary": {"total": 5, "passed": 5},
            "tests": [{"nodeid": "tests/e2e/t.py::C::test_b", "outcome": "passed"}],
        }), encoding="utf-8")
        return a, b

    def test_cong_don_so_lieu(self, hai_tep):
        gop = collect.doc_nhieu_bao_cao(hai_tep)
        tt = collect.tom_tat(gop)
        assert tt["tong"] == 15          # 10 + 5
        assert tt["dat"] == 14           # 9 + 5
        assert tt["hong"] == 1
        assert tt["thoi_gian"] == 35.0   # 5 + 30

    def test_gom_du_cac_ca_tu_moi_tep(self, hai_tep):
        gop = collect.doc_nhieu_bao_cao(hai_tep)
        assert len(gop["tests"]) == 2

    def test_mot_tep_thi_tra_ve_nguyen_ven(self, hai_tep):
        a, _ = hai_tep
        assert collect.doc_nhieu_bao_cao([a]) == collect.doc_bao_cao(a)

    def test_thieu_mot_tep_thi_bao_loi_ro_rang(self, hai_tep, tmp_path):
        a, _ = hai_tep
        with pytest.raises(FileNotFoundError):
            collect.doc_nhieu_bao_cao([a, tmp_path / "khong-co.json"])


class TestGomNhom:
    def test_gop_cac_loi_cung_ban_chat(self, bao_cao_mau):
        """assert 2 == 1 và assert 4 == 1 là cùng một bản chất lỗi."""
        nhom = collect.gom_nhom(collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau)))
        assert len(nhom) == 2
        assert nhom[0].so_luong == 2          # nhóm đông nhất xếp trước
        assert nhom[0].loai_loi == "AssertionError"

    def test_khong_gop_loi_khac_ban_chat(self, bao_cao_mau):
        nhom = collect.gom_nhom(collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau)))
        assert {n.loai_loi for n in nhom} == {"AssertionError", "TimeoutError"}

    def test_chuan_hoa_bo_phan_thay_doi(self):
        a = collect.chuan_hoa("Timeout 30000ms tại 0x7f3a lúc 2026-09-04 10:00:00")
        b = collect.chuan_hoa("Timeout 5000ms tại 0x9b2c lúc 2026-09-05 11:30:00")
        assert a == b

    def test_van_tay_on_dinh(self, bao_cao_mau):
        """Chạy lại cùng dữ liệu phải cho cùng vân tay, để so sánh lịch sử có nghĩa."""
        lan1 = collect.gom_nhom(collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau)))
        lan2 = collect.gom_nhom(collect.trich_ca_loi(collect.doc_bao_cao(bao_cao_mau)))
        assert [n.van_tay for n in lan1] == [n.van_tay for n in lan2]

    def test_khong_co_loi_thi_khong_co_nhom(self):
        assert collect.gom_nhom([]) == []


# ============================================================================
# SO SÁNH VỚI LẦN CHẠY TRƯỚC
# ============================================================================
class TestLichSu:
    def test_lan_dau_chay_chua_co_lich_su(self, tmp_path):
        assert history.lan_truoc(tmp_path / "chua-co.json") is None

    def test_ghi_va_doc_lai(self, tmp_path):
        tep = tmp_path / "ls.json"
        history.ghi_nhan({"tong": 10, "dat": 8, "hong": 2, "bo_qua": 0, "thoi_gian": 1.0},
                         ["aaa", "bbb"], tep)
        truoc = history.lan_truoc(tep)
        assert truoc["hong"] == 2
        assert truoc["van_tay_loi"] == ["aaa", "bbb"]

    def test_thoi_diem_luu_dang_doc_duoc(self, tmp_path):
        """Dấu thời gian phải là ISO đọc được, không phải số epoch của pytest."""
        tep = tmp_path / "ls.json"
        history.ghi_nhan(
            {"tong": 1, "dat": 1, "hong": 0, "bo_qua": 0, "thoi_gian": 1.0,
             "thoi_diem": 1788575773.59},          # dấu thời gian thô từ pytest
            [], tep,
        )
        luu = history.lan_truoc(tep)["thoi_diem"]
        assert isinstance(luu, str) and luu[:2] == "20"   # dạng 2026-09-05T...

    def test_nhan_dien_loi_moi_va_loi_da_sua(self):
        truoc = {"hong": 2, "thoi_gian": 10.0, "van_tay_loi": ["cu1", "chung"]}
        kq = history.so_sanh({"hong": 2, "thoi_gian": 12.0}, ["chung", "moi1"], truoc)
        assert kq["loi_moi"] == ["moi1"]
        assert kq["loi_da_sua"] == ["cu1"]
        assert kq["loi_con_ton"] == ["chung"]
        assert kq["chenh_lech_thoi_gian"] == 2.0

    def test_khong_co_lan_truoc_thi_moi_loi_deu_la_moi(self):
        kq = history.so_sanh({"hong": 1, "thoi_gian": 1.0}, ["x"], None)
        assert kq["co_lan_truoc"] is False
        assert kq["loi_moi"] == ["x"]

    def test_chi_giu_so_lan_gioi_han(self, tmp_path):
        tep = tmp_path / "ls.json"
        for i in range(history.SO_LAN_LUU + 5):
            history.ghi_nhan({"tong": 1, "dat": 1, "hong": 0, "bo_qua": 0, "thoi_gian": 0.1},
                             [f"v{i}"], tep)
        assert len(json.loads(tep.read_text())) == history.SO_LAN_LUU

    def test_tep_lich_su_hong_khong_lam_gay_quy_trinh(self, tmp_path):
        tep = tmp_path / "hong.json"
        tep.write_text("{{{ không phải JSON", encoding="utf-8")
        assert history.lan_truoc(tep) is None


# ============================================================================
# XUẤT BÁO CÁO
# ============================================================================
class TestXuatBaoCao:
    @pytest.fixture
    def du_lieu(self, bao_cao_mau):
        bc = collect.doc_bao_cao(bao_cao_mau)
        nhom = [collect.sang_dict(n) for n in collect.gom_nhom(collect.trich_ca_loi(bc))]
        xu_huong = history.so_sanh(collect.tom_tat(bc), [n["van_tay"] for n in nhom], None)
        return collect.tom_tat(bc), nhom, xu_huong

    def test_xuat_du_hai_dinh_dang(self, du_lieu, tmp_path):
        tt, nhom, xh = du_lieu
        duong_dan = render.ghi_bao_cao(tmp_path, tt, nhom, None, xh)
        assert duong_dan["markdown"].exists()
        assert duong_dan["html"].exists()

    def test_bao_cao_khong_lo_thong_tin_nhay_cam(self, du_lieu, tmp_path):
        tt, nhom, xh = du_lieu
        duong_dan = render.ghi_bao_cao(tmp_path, tt, nhom, None, xh)
        for tep in duong_dan.values():
            assert "SieuBiMat99" not in tep.read_text(encoding="utf-8")

    def test_luon_kem_traceback_goc(self, du_lieu):
        """Người đọc phải tự kiểm chứng được, không chỉ tin lời AI."""
        tt, nhom, xh = du_lieu
        md = render.dung_markdown(tt, nhom, None, xh)
        assert "traceback gốc" in md.lower()
        assert "AssertionError" in md

    def test_canh_bao_ai_co_the_sai(self, du_lieu):
        tt, nhom, xh = du_lieu
        md = render.dung_markdown(tt, nhom, None, xh)
        assert "có thể sai" in md

    def test_bao_khi_chua_bat_ai(self, du_lieu):
        tt, nhom, xh = du_lieu
        assert "DEEPSEEK_API_KEY" in render.dung_markdown(tt, nhom, None, xh)

    def test_tat_ca_dat_thi_bao_cao_bao_thanh_cong(self, tmp_path):
        tt = {"tong": 293, "dat": 293, "hong": 0, "bo_qua": 0, "thoi_gian": 40.0, "thoi_diem": 0}
        xh = history.so_sanh(tt, [], None)
        md = render.dung_markdown(tt, [], None, xh)
        assert "TẤT CẢ ĐỀU ĐẠT" in md

    def test_html_hop_le(self, du_lieu):
        tt, nhom, xh = du_lieu
        h = render.dung_html(tt, nhom, None, xh)
        assert h.startswith("<!doctype html>")
        assert h.rstrip().endswith("</html>")


# ============================================================================
# AN TOÀN KHI GỌI API
# ============================================================================
class TestChonNhaCungCap:
    """Công cụ hỗ trợ cả DeepSeek lẫn Claude, chọn theo khoá API đang có."""

    KHOA = ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "AI_PROVIDER")

    @pytest.fixture(autouse=True)
    def xoa_bien_moi_truong(self, monkeypatch):
        for k in self.KHOA:
            monkeypatch.delenv(k, raising=False)

    def test_chua_co_khoa_nao(self):
        from tools.ai_report import analyze
        assert analyze.nha_cung_cap() is None
        assert analyze.co_khoa_api() is False

    def test_tu_nhan_deepseek(self, monkeypatch):
        from tools.ai_report import analyze
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-gia-lap")
        assert analyze.nha_cung_cap() == "deepseek"
        assert analyze.co_khoa_api() is True

    def test_tu_nhan_claude(self, monkeypatch):
        from tools.ai_report import analyze
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-gia-lap")
        assert analyze.nha_cung_cap() == "claude"

    def test_co_ca_hai_thi_uu_tien_deepseek(self, monkeypatch):
        from tools.ai_report import analyze
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-gia-lap")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-gia-lap")
        assert analyze.nha_cung_cap() == "deepseek"

    def test_bien_AI_PROVIDER_thang_tat_ca(self, monkeypatch):
        from tools.ai_report import analyze
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-gia-lap")
        monkeypatch.setenv("AI_PROVIDER", "claude")
        assert analyze.nha_cung_cap() == "claude"

    def test_gia_tri_AI_PROVIDER_la_bi_bo_qua(self, monkeypatch):
        """Đặt sai tên nhà cung cấp thì quay về tự phát hiện, không gãy."""
        from tools.ai_report import analyze
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-gia-lap")
        monkeypatch.setenv("AI_PROVIDER", "khong-ton-tai")
        assert analyze.nha_cung_cap() == "deepseek"


class TestXuLyPhanHoiDeepSeek:
    """DeepSeek bảo đảm trả về JSON hợp lệ nhưng KHÔNG bảo đảm đúng lược đồ.

    Vì vậy phải kiểm tra lại bằng Pydantic. Nhóm test này giả lập phản hồi để
    kiểm chứng đường xử lý mà không cần gọi API thật.
    """

    @staticmethod
    def _gia_lap(monkeypatch, noi_dung_tra_ve: str):
        """Thay client OpenAI bằng đối tượng giả trả về chuỗi cho trước."""
        import openai

        class _TinNhan:
            content = noi_dung_tra_ve

        class _LuaChon:
            message = _TinNhan()

        class _PhanHoi:
            choices = [_LuaChon()]

        class _Completions:
            @staticmethod
            def create(**_):
                return _PhanHoi()

        class _Chat:
            completions = _Completions()

        class _Client:
            def __init__(self, **_):
                self.chat = _Chat()

        monkeypatch.setattr(openai, "OpenAI", _Client)
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-gia-lap")
        monkeypatch.delenv("AI_PROVIDER", raising=False)

    @pytest.fixture
    def nhom_sach(self):
        return [{
            "van_tay": "abc123", "loai_loi": "AssertionError", "thong_diep": "assert 2 == 1",
            "so_luong": 2, "cac_tang": ["unit"],
            "cac_ca": [{"ten": "test_fifo", "traceback": "assert 2 == 1"}],
        }]

    def test_phan_hoi_dung_luoc_do(self, monkeypatch, nhom_sach):
        from tools.ai_report import analyze

        hop_le = json.dumps({
            "nhan_dinh_chung": "Lỗi tập trung ở nghiệp vụ xuất kho.",
            "cac_nhom": [{
                "van_tay": "abc123", "tieu_de": "Xuất kho sai thứ tự lô",
                "nguyen_nhan": "Có thể thứ tự sắp xếp theo hạn dùng bị đảo.",
                "muc_do": "cao", "do_tin_cay": "trung bình",
                "loi_o_dau": "mã nguồn ứng dụng",
                "huong_sua": "Kiểm tra order_by trong allocate_stock.",
                "tep_can_xem": ["apps/inventory/services.py"],
            }],
        }, ensure_ascii=False)
        self._gia_lap(monkeypatch, hop_le)

        kq = analyze.phan_tich(nhom_sach, {"tong": 293})
        assert kq.cac_nhom[0].van_tay == "abc123"
        assert kq.cac_nhom[0].muc_do == "cao"

    def test_phan_hoi_sai_luoc_do_bi_tu_choi(self, monkeypatch, nhom_sach):
        """AI trả về JSON hợp lệ nhưng thiếu trường bắt buộc thì phải báo lỗi rõ ràng."""
        from pydantic import ValidationError

        from tools.ai_report import analyze

        self._gia_lap(monkeypatch, '{"nhan_dinh_chung": "thiếu mất danh sách nhóm"}')
        with pytest.raises(ValidationError):
            analyze.phan_tich(nhom_sach, {"tong": 293})

    def test_muc_do_ngoai_danh_sach_bi_tu_choi(self, monkeypatch, nhom_sach):
        from pydantic import ValidationError

        from tools.ai_report import analyze

        sai = json.dumps({
            "nhan_dinh_chung": "x",
            "cac_nhom": [{
                "van_tay": "abc123", "tieu_de": "y", "nguyen_nhan": "z",
                "muc_do": "cực kỳ nghiêm trọng",          # không nằm trong danh sách cho phép
                "do_tin_cay": "cao", "loi_o_dau": "bài test", "huong_sua": "w",
            }],
        }, ensure_ascii=False)
        self._gia_lap(monkeypatch, sai)
        with pytest.raises(ValidationError):
            analyze.phan_tich(nhom_sach, {"tong": 293})


class TestRaoChanBaoMat:
    def test_dung_lai_neu_con_sot_thong_tin_nhay_cam(self, monkeypatch):
        """Rào chắn cuối: phát hiện sót thì DỪNG, tuyệt đối không gửi đi."""
        from tools.ai_report import analyze

        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-gia-lap-de-test")
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        nhom_ban = [{
            "van_tay": "x", "loai_loi": "Loi", "thong_diep": "m", "so_luong": 1,
            "cac_tang": ["unit"],
            "cac_ca": [{"ten": "t", "traceback": "DB_PASSWORD=chua_loc_gi_ca"}],
        }]
        with pytest.raises(analyze.LoiBaoMat):
            analyze.phan_tich(nhom_ban, {"tong": 1})

    def test_khong_co_khoa_api_thi_tra_ve_none(self, monkeypatch):
        from tools.ai_report import analyze

        for k in ("DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "AI_PROVIDER"):
            monkeypatch.delenv(k, raising=False)
        assert analyze.phan_tich([{"van_tay": "x"}], {}) is None

    def test_khong_co_loi_thi_khong_goi_api(self):
        from tools.ai_report import analyze

        assert analyze.phan_tich([], {"tong": 293}) is None
