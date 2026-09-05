"""Lọc bỏ thông tin nhạy cảm TRƯỚC KHI gửi log ra dịch vụ bên ngoài.

Log kiểm thử có thể vô tình chứa mật khẩu SQL Server, khoá API, token phiên
hoặc đường dẫn lộ tên người dùng. Module này thay chúng bằng nhãn thay thế.

Nguyên tắc: **thà lọc nhầm còn hơn bỏ sót**. Nếu một chuỗi trông giống thông
tin bí mật thì che đi, kể cả khi có thể nó vô hại.
"""
from __future__ import annotations

import re
from typing import Iterable

#: Nhãn dùng để thay thế mọi thông tin nhạy cảm
NHAN_CHE = "[ĐÃ-CHE"

#: Các mẫu nhận diện thông tin nhạy cảm. Mỗi phần tử: (tên, biểu thức, nhãn thay thế)
QUY_TAC: list[tuple[str, re.Pattern[str], str]] = [
    # Khoá API của Anthropic và các dịch vụ tương tự
    ("khoá API", re.compile(r"sk-[A-Za-z0-9_\-]{16,}"), "[ĐÃ-CHE:khoá-API]"),
    # Chuỗi kết nối ODBC / SQL Server
    ("mật khẩu chuỗi kết nối", re.compile(r"(?i)\b(PWD|PASSWORD)\s*=\s*[^;\s'\"]+"), r"\1=[ĐÃ-CHE]"),
    ("tài khoản chuỗi kết nối", re.compile(r"(?i)\b(UID|USER\s*ID)\s*=\s*[^;\s'\"]+"), r"\1=[ĐÃ-CHE]"),
    # Tham số có dấu nháy phải xử lý TRƯỚC quy tắc chung bên dưới,
    # nếu không dấu nháy mở sẽ bị nuốt mất và chuỗi kết quả bị lệch.
    ("tham số mật khẩu",
     re.compile(r"(?i)\b(password|passwd|pwd|secret|token|api_key)\s*=\s*['\"][^'\"]*['\"]"),
     r"\1='[ĐÃ-CHE]'"),
    # Cặp khoá-giá trị trong .env hoặc log
    ("biến môi trường bí mật",
     re.compile(r"(?i)\b([A-Z_]*(PASSWORD|SECRET|TOKEN|API_KEY|APIKEY)[A-Z_]*)\s*[=:]\s*['\"]?(?!\[ĐÃ-CHE)[^\s'\",;}]+"),
     r"\1=[ĐÃ-CHE]"),
    # JWT
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}"), "[ĐÃ-CHE:JWT]"),
    # Đường dẫn lộ tên người dùng
    ("đường dẫn Windows", re.compile(r"(?i)([A-Z]:\\Users\\)[^\\\s'\"]+"), r"\1[ĐÃ-CHE:người-dùng]"),
    ("đường dẫn Unix", re.compile(r"(/(?:home|Users)/)[^/\s'\"]+"), r"\1[ĐÃ-CHE:người-dùng]"),
    # Cookie phiên của Django
    ("cookie phiên", re.compile(r"(?i)\b(sessionid|csrftoken)\s*[=:]\s*['\"]?[A-Za-z0-9]{16,}"),
     r"\1=[ĐÃ-CHE]"),
    # Địa chỉ email thật (giữ lại các email ...@test.vn / example.com dùng trong test)
    ("email",
     re.compile(r"\b[A-Za-z0-9._%+\-]+@(?!test\.vn\b|example\.(com|org)\b)[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
     "[ĐÃ-CHE:email]"),
]


def loc_van_ban(noi_dung: str | None) -> str:
    """Che mọi thông tin nhạy cảm trong một chuỗi."""
    if not noi_dung:
        return ""
    ket_qua = noi_dung
    for _, mau, thay_the in QUY_TAC:
        ket_qua = mau.sub(thay_the, ket_qua)
    return ket_qua


def loc_du_lieu(du_lieu):
    """Che thông tin nhạy cảm trong cấu trúc lồng nhau (dict / list / str)."""
    if isinstance(du_lieu, str):
        return loc_van_ban(du_lieu)
    if isinstance(du_lieu, dict):
        return {k: loc_du_lieu(v) for k, v in du_lieu.items()}
    if isinstance(du_lieu, (list, tuple)):
        return type(du_lieu)(loc_du_lieu(x) for x in du_lieu)
    return du_lieu


def kiem_tra_con_sot(noi_dung: str) -> list[str]:
    """Trả về tên các quy tắc vẫn còn khớp — dùng để tự kiểm tra sau khi lọc.

    Danh sách rỗng nghĩa là đã sạch.
    """
    con_sot = []
    for ten, mau, _ in QUY_TAC:
        for khop in mau.finditer(noi_dung):
            # Bỏ qua chỗ đã che: mẫu vẫn khớp phần "PWD=" của "PWD=[ĐÃ-CHE]"
            if NHAN_CHE not in khop.group(0):
                con_sot.append(ten)
                break
    return con_sot


def thong_ke(truoc: str, sau: str) -> dict[str, int]:
    """Đếm số chỗ đã che, phục vụ báo cáo minh bạch."""
    return {
        "so_ky_tu_truoc": len(truoc),
        "so_ky_tu_sau": len(sau),
        "so_cho_da_che": sau.count("[ĐÃ-CHE"),
    }
