"""Lưu lịch sử các lần chạy để so sánh xu hướng giữa hai lần liên tiếp."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

TEP_LICH_SU = Path("reports/lich-su-chay.json")
SO_LAN_LUU = 20


def _doc(duong_dan: Path) -> list[dict]:
    if not duong_dan.exists():
        return []
    try:
        return json.loads(duong_dan.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []   # tệp hỏng thì bỏ qua, không làm gãy cả quy trình


def lan_truoc(duong_dan: Path = TEP_LICH_SU) -> dict | None:
    """Lần chạy gần nhất đã lưu, hoặc None nếu đây là lần đầu."""
    lich_su = _doc(duong_dan)
    return lich_su[-1] if lich_su else None


def ghi_nhan(tom_tat: dict, van_tay_loi: list[str],
             duong_dan: Path = TEP_LICH_SU) -> None:
    """Ghi lại lần chạy hiện tại, chỉ giữ SO_LAN_LUU lần gần nhất."""
    lich_su = _doc(duong_dan)
    lich_su.append({
        # Trải tom_tat TRƯỚC: nó cũng có khoá "thoi_diem" (dấu thời gian thô của
        # pytest). Đặt sau sẽ bị ghi đè và báo cáo hiện số epoch khó đọc.
        **tom_tat,
        "thoi_diem": datetime.now().isoformat(timespec="seconds"),
        "van_tay_loi": sorted(van_tay_loi),
    })
    duong_dan.parent.mkdir(parents=True, exist_ok=True)
    duong_dan.write_text(
        json.dumps(lich_su[-SO_LAN_LUU:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def so_sanh(hien_tai: dict, van_tay_hien_tai: list[str],
            truoc: dict | None) -> dict:
    """So sánh lần chạy hiện tại với lần trước.

    Trả về: lỗi MỚI xuất hiện, lỗi ĐÃ SỬA XONG, lỗi CÒN TỒN, và chênh lệch số liệu.
    """
    if truoc is None:
        return {
            "co_lan_truoc": False,
            "loi_moi": sorted(van_tay_hien_tai),
            "loi_da_sua": [],
            "loi_con_ton": [],
            "chenh_lech_hong": 0,
            "chenh_lech_thoi_gian": 0.0,
        }

    cu = set(truoc.get("van_tay_loi", []))
    moi = set(van_tay_hien_tai)
    return {
        "co_lan_truoc": True,
        "thoi_diem_truoc": truoc.get("thoi_diem", ""),
        "loi_moi": sorted(moi - cu),
        "loi_da_sua": sorted(cu - moi),
        "loi_con_ton": sorted(moi & cu),
        "chenh_lech_hong": hien_tai["hong"] - truoc.get("hong", 0),
        "chenh_lech_thoi_gian": round(hien_tai["thoi_gian"] - truoc.get("thoi_gian", 0.0), 2),
    }
