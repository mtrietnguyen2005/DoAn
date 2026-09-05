"""Gửi log lỗi ĐÃ LỌC cho Claude và nhận về phân tích có cấu trúc.

Hai nguyên tắc bắt buộc:

1. **Chỉ gửi dữ liệu đã lọc.** Module này tự kiểm tra lần nữa trước khi gửi;
   nếu phát hiện thông tin nhạy cảm còn sót thì dừng và báo lỗi.
2. **Kết quả AI là GỢI Ý, không phải kết luận.** Báo cáo luôn hiển thị
   traceback gốc bên cạnh để người đọc tự kiểm chứng.
"""
from __future__ import annotations

import json
import os
from typing import Literal

from pydantic import BaseModel, Field

from .redact import kiem_tra_con_sot

MODEL = "claude-opus-5"

HUONG_DAN = """Bạn là chuyên gia kiểm thử phần mềm, đang phân tích log lỗi của một
bộ kiểm thử tự động viết bằng pytest cho ứng dụng Django (website bán linh kiện máy tính).

Bộ test có ba tầng:
- unit: logic thuần trong model và service, không qua HTTP
- integration: gọi qua HTTP bằng Django test client (LƯU Ý: mặc định TẮT kiểm tra CSRF)
- e2e: điều khiển trình duyệt thật bằng Playwright

Nghiệp vụ cốt lõi gồm: quản lý tồn kho theo lô hàng, xuất kho FIFO ưu tiên lô hết hạn
sớm nhất, lưu giá vốn COGS bình quân gia quyền tại thời điểm bán, và hoàn trả hàng về
đúng lô ban đầu khi hủy đơn.

Với mỗi NHÓM lỗi được cung cấp, hãy phân tích và trả về JSON theo đúng lược đồ.

Yêu cầu bắt buộc:
- Viết bằng tiếng Việt, ngắn gọn, đi thẳng vào vấn đề.
- Trường `nguyen_nhan` là GIẢ THUYẾT dựa trên traceback, không được khẳng định chắc chắn.
- Trường `do_tin_cay` phản ánh trung thực mức độ chắc chắn của bạn.
- Nếu traceback không đủ dữ kiện, hãy nói rõ là không đủ thay vì suy đoán bừa.
- Phân biệt rõ: lỗi trong MÃ NGUỒN ứng dụng hay lỗi trong CHÍNH BÀI TEST."""


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
    return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


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


def phan_tich(cac_nhom: list[dict], tom_tat: dict) -> KetQuaPhanTich | None:
    """Gọi Claude phân tích các nhóm lỗi.

    Trả về None nếu không có khoá API — khi đó báo cáo vẫn được sinh ra
    nhưng không có phần phân tích của AI.
    """
    if not cac_nhom:
        return None
    if not co_khoa_api():
        return None

    noi_dung = _dung_du_lieu_gui(cac_nhom, tom_tat)

    # Rào chắn cuối cùng: tuyệt đối không gửi đi nếu còn thông tin nhạy cảm
    con_sot = kiem_tra_con_sot(noi_dung)
    if con_sot:
        raise LoiBaoMat(
            "Phát hiện thông tin nhạy cảm chưa được lọc, đã DỪNG không gửi ra ngoài: "
            + ", ".join(con_sot)
        )

    import anthropic

    client = anthropic.Anthropic()
    phan_hoi = client.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=HUONG_DAN,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": f"Đây là kết quả chạy test có lỗi. Hãy phân tích từng nhóm:\n\n{noi_dung}",
        }],
        output_format=KetQuaPhanTich,
    )
    return phan_hoi.parsed_output
