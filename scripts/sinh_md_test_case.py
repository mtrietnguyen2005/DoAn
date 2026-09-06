# -*- coding: utf-8 -*-
"""Sinh docs/DANH-MUC-TEST-CASE.md từ mã nguồn thật (đồng bộ với sinh_excel_test_case.py).

Chạy sau khi đã có tests/**/test_*.py là nguồn chân lý duy nhất — không sửa
tay tệp .md này, sửa test rồi chạy lại script.
"""
import ast
import collections
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
GIAI_DOAN = [
    ("unit", "GIAI ĐOẠN 1 — UNIT TEST"),
    ("integration", "GIAI ĐOẠN 1b — INTEGRATION TEST"),
    ("e2e", "GIAI ĐOẠN 2 — E2E TEST"),
]


def viet_hoa_ten(ten: str) -> str:
    return ten.removeprefix("test_").replace("_", " ").strip().capitalize()


def dem_ca_that(root: pathlib.Path) -> collections.Counter:
    """Đếm số ca chạy thật (kể cả parametrize) bằng pytest --collect-only."""
    ket_qua = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "--tat-ca"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    dem = collections.Counter()
    for dong in ket_qua.stdout.splitlines():
        if "::" not in dong:
            continue
        phan = dong.strip().split("::")
        if len(phan) >= 3:
            ten_ham = phan[2].split("[")[0]
            dem[(phan[0], phan[1], ten_ham)] += 1
    return dem


def main():
    dem = dem_ca_that(ROOT)
    dong_ra = [
        "# 📋 Danh mục toàn bộ Test Case",
        "",
        "> Tài liệu **sinh tự động** từ mã nguồn bằng `scripts/sinh_md_test_case.py`: tên và",
        "> mô tả lấy bằng phân tích cú pháp (AST), số ca lấy từ `pytest --collect-only`.",
        "> Luôn khớp với code thực tế — sửa test rồi chạy lại script, không sửa tay tệp này.",
        "",
    ]

    tong_theo_giai_doan = {}
    noi_dung_giai_doan = {}

    for thu_muc, _ in GIAI_DOAN:
        d = ROOT / "tests" / thu_muc
        phan_noi_dung = []
        tong_giai_doan = 0
        for tep in sorted(d.rglob("test_*.py")):
            nguon = tep.read_text(encoding="utf-8")
            cay = ast.parse(nguon)
            mo_ta_module = ast.get_docstring(cay) or ""
            mo_ta_module = " ".join(mo_ta_module.split())

            cac_lop = [n for n in cay.body if isinstance(n, ast.ClassDef)]
            so_ca_tep = 0
            phan_lop = []
            for lop in cac_lop:
                mo_ta_lop = ast.get_docstring(lop) or ""
                mo_ta_lop = " ".join(mo_ta_lop.split())
                cac_ham = [x for x in lop.body if isinstance(x, ast.FunctionDef)
                          and x.name.startswith("test_")]
                if not cac_ham:
                    continue

                hang_bang = []
                so_ca_lop = 0
                for i, f in enumerate(cac_ham, 1):
                    doc = ast.get_docstring(f) or ""
                    doc = " ".join(doc.split())
                    ten_de_doc = viet_hoa_ten(f.name)
                    so_ca = dem.get((str(tep.relative_to(ROOT)).replace("\\", "/"),
                                     lop.name, f.name), 1)
                    so_ca_lop += so_ca
                    co_lap = any("parametrize" in ast.unparse(dc) for dc in f.decorator_list)
                    co_lap_ky_hieu = " 🔁" if co_lap else ""
                    y_nghia = doc if doc else ten_de_doc
                    hang_bang.append(
                        f"| {i} | `{f.name}`{co_lap_ky_hieu}<br>{ten_de_doc} | {y_nghia} |"
                    )
                so_ca_tep += so_ca_lop

                khoi = [f"#### 🔹 `{lop.name}` — {so_ca_lop} ca", ""]
                if mo_ta_lop:
                    khoi += [f"**Mục đích:** {mo_ta_lop}", ""]
                khoi += ["| # | Test case | Kiểm chứng điều gì |", "|:--:|---|---|"]
                khoi += hang_bang
                khoi += [""]
                phan_lop.append("\n".join(khoi))

            tong_giai_doan += so_ca_tep
            khoi_tep = [f"### 📄 `{tep.name}` — {so_ca_tep} ca", ""]
            if mo_ta_module:
                khoi_tep += [f"> {mo_ta_module}", ""]
            khoi_tep += [""]
            phan_noi_dung.append("\n".join(khoi_tep) + "\n\n".join(phan_lop))

        tong_theo_giai_doan[thu_muc] = tong_giai_doan
        noi_dung_giai_doan[thu_muc] = phan_noi_dung

    tong_cong = sum(tong_theo_giai_doan.values())
    ten_hien_thi = {"unit": "Unit", "integration": "Integration", "e2e": "E2E (Playwright)"}

    dong_ra.append(f"**Tổng cộng: {tong_cong} ca kiểm thử** "
                    f"({tong_theo_giai_doan['unit']} Unit + "
                    f"{tong_theo_giai_doan['integration']} Integration + "
                    f"{tong_theo_giai_doan['e2e']} E2E)")
    dong_ra.append("")
    dong_ra.append("| Giai đoạn | Số ca |")
    dong_ra.append("|---|---|")
    for thu_muc, _ in GIAI_DOAN:
        dong_ra.append(f"| {ten_hien_thi[thu_muc]} | {tong_theo_giai_doan[thu_muc]} |")
    dong_ra.append(f"| **Tổng** | **{tong_cong}** |")
    dong_ra += ["", "", "---", ""]

    for thu_muc, tieu_de in GIAI_DOAN:
        dong_ra.append(f"## {tieu_de} — {tong_theo_giai_doan[thu_muc]} ca")
        dong_ra.append("")
        dong_ra.append("\n\n".join(noi_dung_giai_doan[thu_muc]))
        dong_ra += ["", "---", ""]

    dong_ra.append("> 🔁 = test chạy lặp với nhiều bộ dữ liệu (`@pytest.mark.parametrize`)")

    out = ROOT / "docs" / "DANH-MUC-TEST-CASE.md"
    out.write_text("\n".join(dong_ra) + "\n", encoding="utf-8")
    print(f"✓ {out}  |  {tong_cong} ca kiểm thử")


if __name__ == "__main__":
    main()
