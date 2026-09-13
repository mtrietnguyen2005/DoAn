from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .redact import loc_van_ban

THU_MUC_ANH = Path("tests/e2e/screenshots")

GIOI_HAN_TRACEBACK = 4000

CHUAN_HOA = [
    (re.compile(r"0x[0-9a-fA-F]+"), "0xĐỊA_CHỈ"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}[^\s'\"]*"), "<thời-điểm>"),
    (re.compile(r"\bDH\d{11,}\b"), "<mã-đơn>"),
    (re.compile(r"\bhttp://[^\s'\"]+"), "<địa-chỉ>"),
    (re.compile(r"line \d+"), "line <n>"),
    (re.compile(r"\b\d+"), "<số>"),
]


@dataclass
class CaLoi:

    ma: str
    tep: str
    lop: str
    ten: str
    tang: str
    giai_doan: str
    loai_loi: str
    thong_diep: str
    traceback: str
    thoi_gian: float = 0.0
    anh_chup: str | None = None

    @property
    def van_tay(self) -> str:
        goc = f"{self.loai_loi}|{chuan_hoa(self.thong_diep)}"
        return hashlib.sha1(goc.encode("utf-8")).hexdigest()[:10]


@dataclass
class NhomLoi:

    van_tay: str
    loai_loi: str
    thong_diep_dai_dien: str
    cac_ca: list[CaLoi] = field(default_factory=list)

    @property
    def so_luong(self) -> int:
        return len(self.cac_ca)

    @property
    def cac_tang(self) -> list[str]:
        return sorted({c.tang for c in self.cac_ca})


def chuan_hoa(van_ban: str) -> str:
    ket_qua = van_ban or ""
    for mau, thay in CHUAN_HOA:
        ket_qua = mau.sub(thay, ket_qua)
    return ket_qua.strip()


def _tang_tu_duong_dan(duong_dan: str) -> str:
    for t in ("unit", "integration", "e2e"):
        if f"/{t}/" in duong_dan or f"\\{t}\\" in duong_dan:
            return t
    return "khác"


def _tim_anh(ten_test: str) -> str | None:
    if not THU_MUC_ANH.exists():
        return None
    goc = ten_test.split("[")[0]
    for anh in THU_MUC_ANH.glob("*.png"):
        if anh.stem.startswith(goc):
            return str(anh)
    return None


def doc_bao_cao(duong_dan: str | Path) -> dict:
    duong_dan = Path(duong_dan)
    if not duong_dan.exists():
        raise FileNotFoundError(
            f"Không tìm thấy {duong_dan}. Hãy chạy trước:\n"
            f"  pytest --json-report --json-report-file={duong_dan}"
        )
    return json.loads(duong_dan.read_text(encoding="utf-8"))


def doc_nhieu_bao_cao(cac_duong_dan) -> dict:
    cac_bao_cao = [doc_bao_cao(d) for d in cac_duong_dan]
    if len(cac_bao_cao) == 1:
        return cac_bao_cao[0]

    gop = {"tests": [], "summary": {}, "duration": 0.0,
           "created": max(b.get("created", 0) for b in cac_bao_cao)}
    for b in cac_bao_cao:
        gop["tests"].extend(b.get("tests", []))
        gop["duration"] += b.get("duration", 0.0)
        for khoa, gia_tri in b.get("summary", {}).items():
            if isinstance(gia_tri, (int, float)):
                gop["summary"][khoa] = gop["summary"].get(khoa, 0) + gia_tri
    return gop


def trich_ca_loi(bao_cao: dict) -> list[CaLoi]:
    ket_qua: list[CaLoi] = []
    for ca in bao_cao.get("tests", []):
        if ca.get("outcome") not in ("failed", "error"):
            continue
        for giai_doan in ("call", "setup", "teardown"):
            chi_tiet = ca.get(giai_doan)
            if not chi_tiet or chi_tiet.get("outcome") not in ("failed", "error"):
                continue

            tb_tho = chi_tiet.get("longrepr") or ""
            dong_cuoi = tb_tho.strip().splitlines()[-1] if tb_tho.strip() else ""
            thong_diep = re.sub(r"^E\s+", "", dong_cuoi).strip() or "(không có thông báo)"
            loai = thong_diep.split(":")[0].strip() if ":" in thong_diep else "Lỗi không rõ loại"

            ma = ca["nodeid"]
            phan = ma.split("::")
            ket_qua.append(CaLoi(
                ma=ma,
                tep=phan[0],
                lop=phan[1] if len(phan) > 2 else "",
                ten=phan[-1],
                tang=_tang_tu_duong_dan(phan[0]),
                giai_doan=giai_doan,
                loai_loi=loc_van_ban(loai)[:120],
                thong_diep=loc_van_ban(thong_diep)[:500],
                traceback=loc_van_ban(tb_tho)[-GIOI_HAN_TRACEBACK:],
                thoi_gian=round(ca.get("duration", 0.0), 3),
                anh_chup=_tim_anh(phan[-1]),
            ))
            break
    return ket_qua


def gom_nhom(cac_ca: list[CaLoi]) -> list[NhomLoi]:
    theo_van_tay: dict[str, NhomLoi] = {}
    for ca in cac_ca:
        nhom = theo_van_tay.get(ca.van_tay)
        if nhom is None:
            nhom = NhomLoi(van_tay=ca.van_tay, loai_loi=ca.loai_loi,
                           thong_diep_dai_dien=ca.thong_diep)
            theo_van_tay[ca.van_tay] = nhom
        nhom.cac_ca.append(ca)
    return sorted(theo_van_tay.values(), key=lambda n: -n.so_luong)


def tom_tat(bao_cao: dict) -> dict:
    tk = bao_cao.get("summary", {})
    return {
        "tong": tk.get("total", 0),
        "dat": tk.get("passed", 0),
        "hong": tk.get("failed", 0) + tk.get("error", 0),
        "bo_qua": tk.get("skipped", 0),
        "thoi_gian": round(bao_cao.get("duration", 0.0), 2),
        "thoi_diem": bao_cao.get("created", 0),
    }


def sang_dict(nhom: NhomLoi) -> dict:
    return {
        "van_tay": nhom.van_tay,
        "loai_loi": nhom.loai_loi,
        "thong_diep": nhom.thong_diep_dai_dien,
        "so_luong": nhom.so_luong,
        "cac_tang": nhom.cac_tang,
        "cac_ca": [asdict(c) for c in nhom.cac_ca],
    }
