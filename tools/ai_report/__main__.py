from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from . import analyze, collect, history, render


def main(argv: list[str] | None = None) -> int:
    bp = argparse.ArgumentParser(
        prog="python -m tools.ai_report",
        description="Phân tích log lỗi kiểm thử bằng AI và xuất báo cáo.",
    )
    bp.add_argument("--input", nargs="+", default=["reports/ket-qua.json"],
                    help="một hoặc nhiều tệp JSON kết quả pytest (nhiều tệp sẽ được gộp)")
    bp.add_argument("--out", default="reports", help="thư mục xuất báo cáo")
    bp.add_argument("--no-ai", action="store_true", help="không gọi API, chỉ gom nhóm")
    tham_so = bp.parse_args(argv)

    try:
        bao_cao = collect.doc_nhieu_bao_cao(tham_so.input)
    except FileNotFoundError as loi:
        print(f"❌ {loi}", file=sys.stderr)
        return 2

    tom_tat = collect.tom_tat(bao_cao)
    if len(tham_so.input) > 1:
        print(f"🔗 Đã gộp {len(tham_so.input)} tệp kết quả")
    print(f"📊 {tom_tat['tong']} ca · {tom_tat['dat']} đạt · {tom_tat['hong']} thất bại "
          f"· {tom_tat['thoi_gian']}s")

    cac_ca = collect.trich_ca_loi(bao_cao)
    nhom = collect.gom_nhom(cac_ca)
    cac_nhom = [collect.sang_dict(n) for n in nhom]
    if cac_ca:
        print(f"🔍 Gom {len(cac_ca)} ca thất bại thành {len(nhom)} nhóm nguyên nhân")
        co_anh = sum(1 for c in cac_ca if c.anh_chup)
        if co_anh:
            print(f"📸 Đính kèm {co_anh} ảnh chụp màn hình")

    van_tay = [n["van_tay"] for n in cac_nhom]
    xu_huong = history.so_sanh(tom_tat, van_tay, history.lan_truoc())
    if xu_huong["co_lan_truoc"]:
        print(f"📈 So lần trước: {xu_huong['chenh_lech_hong']:+d} ca hỏng · "
              f"{len(xu_huong['loi_moi'])} lỗi mới · {len(xu_huong['loi_da_sua'])} lỗi đã hết")

    ket_qua_ai = None
    if cac_nhom and not tham_so.no_ai:
        if not analyze.co_khoa_api():
            print("⚠️  Chưa cấu hình khoá API — bỏ qua bước phân tích AI.\n"
                  "    Đặt DEEPSEEK_API_KEY rồi chạy lại.")
        else:
            print(f"🧠 Đang nhờ DeepSeek ({analyze.MODEL_DEEPSEEK}) "
                  f"phân tích {len(cac_nhom)} nhóm lỗi...")
            try:
                ket_qua_ai = analyze.phan_tich(cac_nhom, tom_tat)
                print("✅ Phân tích xong")
            except analyze.LoiBaoMat as loi:
                print(f"🛑 {loi}", file=sys.stderr)
                return 3
            except ValidationError as loi:
                print(f"⚠️  AI trả về dữ liệu sai lược đồ: {loi.error_count()} lỗi. "
                      "Vẫn xuất báo cáo phần gom nhóm.", file=sys.stderr)
            except Exception as loi:                       # noqa: BLE001
                print(f"⚠️  Gọi API thất bại ({type(loi).__name__}: {loi}). "
                      "Vẫn xuất báo cáo phần gom nhóm.", file=sys.stderr)

    duong_dan = render.ghi_bao_cao(Path(tham_so.out), tom_tat, cac_nhom, ket_qua_ai, xu_huong)
    history.ghi_nhan(tom_tat, van_tay)

    print(f"\n📄 Markdown: {duong_dan['markdown']}")
    print(f"🌐 HTML    : {duong_dan['html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
