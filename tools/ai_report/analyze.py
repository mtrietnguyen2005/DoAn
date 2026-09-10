"""Gửi log lỗi ĐÃ LỌC cho DeepSeek và nhận về phân tích có cấu trúc.

Dùng SDK ``openai`` trỏ tới ``api.deepseek.com`` — DeepSeek cung cấp API
tương thích chuẩn OpenAI nên không cần SDK riêng.

Hai nguyên tắc bắt buộc:

1. **Chỉ gửi dữ liệu đã lọc.** Module này kiểm tra lại lần nữa trước khi gửi;
   phát hiện thông tin nhạy cảm còn sót thì DỪNG, không gửi.
2. **Kết quả AI là GỢI Ý, không phải kết luận.** Báo cáo luôn hiển thị
   traceback gốc bên cạnh để người đọc tự kiểm chứng.
"""
from __future__ import annotations

import json
import os
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from .redact import kiem_tra_con_sot

DIA_CHI_DEEPSEEK = "https://api.deepseek.com"
MODEL_DEEPSEEK = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

HUONG_DAN = """Bạn là chuyên gia kiểm thử phần mềm, đang phân tích log lỗi của một
bộ kiểm thử tự động viết bằng pytest cho ứng dụng Django (website bán linh kiện máy tính).

Bộ test có ba tầng:
- unit: logic thuần trong model và service, không qua HTTP
- integration: gọi qua HTTP bằng Django test client (LƯU Ý: mặc định TẮT kiểm tra CSRF)
- e2e: điều khiển trình duyệt thật bằng Playwright

Nghiệp vụ cốt lõi gồm: quản lý tồn kho theo lô hàng, xuất kho FIFO ưu tiên lô có ngày
nhập kho sớm nhất, lưu giá vốn COGS bình quân gia quyền tại thời điểm bán, và hoàn trả hàng về
đúng lô ban đầu khi hủy đơn.

Với mỗi NHÓM lỗi được cung cấp, hãy phân tích và trả về kết quả dạng json.

Yêu cầu bắt buộc:
- Viết bằng tiếng Việt, ngắn gọn, đi thẳng vào vấn đề.
- Trường `nguyen_nhan` là GIẢ THUYẾT dựa trên traceback, không được khẳng định chắc chắn.
- Trường `do_tin_cay` phản ánh trung thực mức độ chắc chắn của bạn.
- Nếu traceback không đủ dữ kiện, hãy nói rõ là không đủ thay vì suy đoán bừa.
- Phân biệt rõ: lỗi trong MÃ NGUỒN ứng dụng hay lỗi trong CHÍNH BÀI TEST.
- Trường `van_tay` phải chép NGUYÊN VĂN từ dữ liệu đầu vào, không được tự đặt."""


class PhanTichNhom(BaseModel):
    """Kết quả phân tích một nhóm lỗi."""

    van_tay: str = Field(description="Mã vân tay của nhóm, chép nguyên từ dữ liệu đầu vào")
    tieu_de: str = Field(description="Tóm tắt lỗi trong một câu ngắn")
    nguyen_nhan: str = Field(description="Giả thuyết về nguyên nhân gốc, 2-4 câu")
    muc_do: Literal["nghiêm trọng", "cao", "trung bình", "thấp"]
    do_tin_cay: Literal["cao", "trung bình", "thấp"]
    loi_o_dau: Literal["mã nguồn ứng dụng", "bài test", "môi trường", "chưa xác định"]
    huong_sua: str = Field(description="Gợi ý cách khắc phục, cụ thể và khả thi")
    tep_can_xem: list[str] = Field(default_factory=list,
                                   description="Các tệp nên mở ra xem, tối đa 3")


class KetQuaPhanTich(BaseModel):
    nhan_dinh_chung: str = Field(description="Nhận định tổng quan về lần chạy, 2-3 câu")
    cac_nhom: list[PhanTichNhom]


class LoiBaoMat(Exception):
    """Phát hiện thông tin nhạy cảm còn sót — dừng, không gửi đi."""


def co_khoa_api() -> bool:
    """Đã cấu hình khoá API của DeepSeek chưa."""
    return bool(os.environ.get("DEEPSEEK_API_KEY"))


# ============================================================================
# CHUẨN BỊ DỮ LIỆU GỬI ĐI
# ============================================================================
def _dung_du_lieu_gui(cac_nhom: list[dict], tom_tat: dict) -> str:
    goi = {"tom_tat_lan_chay": tom_tat, "cac_nhom_loi": []}
    for n in cac_nhom:
        goi["cac_nhom_loi"].append({
            "van_tay": n["van_tay"],
            "loai_loi": n["loai_loi"],
            "thong_diep": n["thong_diep"],
            "so_ca_anh_huong": n["so_luong"],
            "cac_tang": n["cac_tang"],
            "ten_cac_ca": [c["ten"] for c in n["cac_ca"][:5]],
            "traceback_dai_dien": n["cac_ca"][0]["traceback"],
        })
    return json.dumps(goi, ensure_ascii=False, indent=2)


def _kiem_tra_an_toan(noi_dung: str) -> None:
    """Rào chắn cuối cùng trước khi dữ liệu rời khỏi máy."""
    con_sot = kiem_tra_con_sot(noi_dung)
    if con_sot:
        raise LoiBaoMat(
            "Phát hiện thông tin nhạy cảm chưa được lọc, đã DỪNG không gửi ra ngoài: "
            + ", ".join(con_sot)
        )


# ============================================================================
# GỌI API
# ============================================================================
def _goi_deepseek(noi_dung: str) -> KetQuaPhanTich:
    """Gọi DeepSeek qua SDK openai (DeepSeek dùng giao thức tương thích OpenAI).

    DeepSeek có chế độ JSON (``response_format``) bảo đảm trả về JSON hợp lệ,
    nhưng KHÔNG bảo đảm đúng lược đồ. Vì vậy phải kiểm tra lại bằng Pydantic.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=DIA_CHI_DEEPSEEK,
    )
    luoc_do = json.dumps(KetQuaPhanTich.model_json_schema(), ensure_ascii=False, indent=2)

    phan_hoi = client.chat.completions.create(
        model=MODEL_DEEPSEEK,
        response_format={"type": "json_object"},
        max_tokens=8000,
        messages=[
            {"role": "system", "content": HUONG_DAN},
            {
                "role": "user",
                "content": (
                    "Đây là kết quả chạy test có lỗi. Hãy phân tích từng nhóm và trả về "
                    "MỘT đối tượng json duy nhất đúng theo lược đồ sau:\n\n"
                    f"```json\n{luoc_do}\n```\n\n"
                    f"Dữ liệu cần phân tích:\n\n{noi_dung}"
                ),
            },
        ],
    )
    van_ban = phan_hoi.choices[0].message.content or "{}"
    return KetQuaPhanTich.model_validate_json(van_ban)


def phan_tich(cac_nhom: list[dict], tom_tat: dict) -> KetQuaPhanTich | None:
    """Nhờ AI phân tích các nhóm lỗi.

    Trả về ``None`` khi không có lỗi nào, hoặc chưa cấu hình khoá API — khi đó
    báo cáo vẫn được sinh ra, chỉ thiếu phần nhận định của AI.

    Ném ``LoiBaoMat`` nếu phát hiện thông tin nhạy cảm còn sót.
    Ném ``ValidationError`` nếu AI trả về dữ liệu sai lược đồ.
    """
    if not cac_nhom or not co_khoa_api():
        return None

    noi_dung = _dung_du_lieu_gui(cac_nhom, tom_tat)
    _kiem_tra_an_toan(noi_dung)
    return _goi_deepseek(noi_dung)
