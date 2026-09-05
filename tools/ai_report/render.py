"""Xuất báo cáo ra Markdown và HTML."""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

MAU_MUC_DO = {
    "nghiêm trọng": ("#991b1b", "#fee2e2"),
    "cao": ("#9a3412", "#ffedd5"),
    "trung bình": ("#854d0e", "#fef9c3"),
    "thấp": ("#065f46", "#d1fae5"),
}


def _phan_tich_theo_van_tay(ket_qua) -> dict:
    if ket_qua is None:
        return {}
    return {p.van_tay: p for p in ket_qua.cac_nhom}


def dung_markdown(tom_tat, cac_nhom, ket_qua_ai, xu_huong) -> str:
    d = []
    d.append("# 🤖 Báo cáo phân tích lỗi kiểm thử")
    d.append("")
    d.append(f"*Sinh lúc {datetime.now():%H:%M %d/%m/%Y}*")
    d.append("")

    # --- Tổng quan ---
    trang_thai = "✅ TẤT CẢ ĐỀU ĐẠT" if tom_tat["hong"] == 0 else f"❌ {tom_tat['hong']} CA THẤT BẠI"
    d.append(f"## {trang_thai}")
    d.append("")
    d.append("| Chỉ số | Giá trị |")
    d.append("|---|---|")
    d.append(f"| Tổng số ca | {tom_tat['tong']} |")
    d.append(f"| Đạt | {tom_tat['dat']} |")
    d.append(f"| Thất bại | {tom_tat['hong']} |")
    d.append(f"| Bỏ qua | {tom_tat['bo_qua']} |")
    d.append(f"| Thời gian chạy | {tom_tat['thoi_gian']}s |")
    d.append("")

    # --- Xu hướng ---
    if xu_huong.get("co_lan_truoc"):
        d.append("## 📈 So với lần chạy trước")
        d.append("")
        d.append(f"*Lần trước: {xu_huong.get('thoi_diem_truoc', '—')}*")
        d.append("")
        c = xu_huong["chenh_lech_hong"]
        if c > 0:
            d.append(f"- 🔺 **Tăng thêm {c} ca thất bại**")
        elif c < 0:
            d.append(f"- 🔻 Giảm được {abs(c)} ca thất bại")
        else:
            d.append("- ➡️ Số ca thất bại không đổi")
        if xu_huong["loi_moi"]:
            d.append(f"- 🆕 **{len(xu_huong['loi_moi'])} lỗi MỚI xuất hiện** — nhiều khả năng do thay đổi vừa rồi")
        if xu_huong["loi_da_sua"]:
            d.append(f"- ✅ {len(xu_huong['loi_da_sua'])} lỗi đã hết")
        if xu_huong["loi_con_ton"]:
            d.append(f"- ⏳ {len(xu_huong['loi_con_ton'])} lỗi vẫn còn từ lần trước")
        d.append("")

    if not cac_nhom:
        d.append("Không có lỗi nào để phân tích. 🎉")
        return "\n".join(d)

    # --- Nhận định của AI ---
    ai = _phan_tich_theo_van_tay(ket_qua_ai)
    if ket_qua_ai is not None:
        d.append("## 🧠 Nhận định chung")
        d.append("")
        d.append(f"> {ket_qua_ai.nhan_dinh_chung}")
        d.append("")
    else:
        d.append("> ⚠️ **Chưa bật phân tích AI.** Đặt biến môi trường `ANTHROPIC_API_KEY`")
        d.append("> để có thêm phần phân tích nguyên nhân. Báo cáo dưới đây vẫn đầy đủ")
        d.append("> thông tin gom nhóm và traceback gốc.")
        d.append("")

    # --- Chi tiết từng nhóm ---
    d.append(f"## 🔍 Chi tiết {len(cac_nhom)} nhóm lỗi")
    d.append("")
    for i, nhom in enumerate(cac_nhom, 1):
        p = ai.get(nhom["van_tay"])
        tieu_de = p.tieu_de if p else nhom["thong_diep"][:90]
        d.append(f"### {i}. {tieu_de}")
        d.append("")
        d.append(f"`{nhom['loai_loi']}` · **{nhom['so_luong']} ca** · tầng: {', '.join(nhom['cac_tang'])}"
                 + (" · 🆕 **mới**" if nhom["van_tay"] in xu_huong.get("loi_moi", []) else ""))
        d.append("")

        if p:
            d.append(f"| | |")
            d.append(f"|---|---|")
            d.append(f"| **Mức độ** | {p.muc_do} |")
            d.append(f"| **Lỗi nằm ở** | {p.loi_o_dau} |")
            d.append(f"| **Độ tin cậy của nhận định** | {p.do_tin_cay} |")
            d.append("")
            d.append(f"**Giả thuyết nguyên nhân (do AI đề xuất):** {p.nguyen_nhan}")
            d.append("")
            d.append(f"**Hướng sửa:** {p.huong_sua}")
            d.append("")
            if p.tep_can_xem:
                d.append("**Nên xem các tệp:** " + ", ".join(f"`{t}`" for t in p.tep_can_xem))
                d.append("")

        d.append("<details><summary>Các ca thất bại và traceback gốc</summary>")
        d.append("")
        for ca in nhom["cac_ca"]:
            d.append(f"- `{ca['ma']}`" + (f" — 📸 `{ca['anh_chup']}`" if ca["anh_chup"] else ""))
        d.append("")
        d.append("```")
        d.append(nhom["cac_ca"][0]["traceback"][-2000:])
        d.append("```")
        d.append("")
        d.append("</details>")
        d.append("")

    d.append("---")
    d.append("")
    d.append("⚠️ **Lưu ý khi đọc báo cáo:** phần *Giả thuyết nguyên nhân* và *Hướng sửa* do AI")
    d.append("suy luận từ traceback, **có thể sai**. Luôn đối chiếu với traceback gốc ở phần")
    d.append("mở rộng trước khi sửa code. Log đã được lọc bỏ mật khẩu, khoá API và đường dẫn")
    d.append("cá nhân trước khi gửi đi phân tích.")
    return "\n".join(d)


def dung_html(tom_tat, cac_nhom, ket_qua_ai, xu_huong) -> str:
    ai = _phan_tich_theo_van_tay(ket_qua_ai)
    e = html.escape
    dat_het = tom_tat["hong"] == 0

    h = [f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo phân tích lỗi kiểm thử</title><style>
*{{box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;margin:0;background:#f8fafc;color:#0f172a;line-height:1.6}}
.bao{{max-width:1000px;margin:0 auto;padding:32px 20px}}
h1{{font-size:26px;margin:0 0 4px}}
.ngay{{color:#64748b;font-size:14px;margin-bottom:24px}}
.the{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:20px;margin-bottom:16px}}
.trang-thai{{font-size:20px;font-weight:700;padding:16px 20px;border-radius:12px;margin-bottom:16px;
  background:{'#d1fae5' if dat_het else '#fee2e2'};color:{'#065f46' if dat_het else '#991b1b'}}}
.so-lieu{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px}}
.o{{text-align:center;padding:14px;background:#f1f5f9;border-radius:10px}}
.o b{{display:block;font-size:24px}}
.nhan{{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin:12px 0}}
td,th{{padding:8px 10px;border-bottom:1px solid #e2e8f0;text-align:left;font-size:14px}}
pre{{background:#0f172a;color:#e2e8f0;padding:14px;border-radius:8px;overflow-x:auto;font-size:12px}}
details{{margin-top:12px}} summary{{cursor:pointer;font-weight:600;color:#2563eb}}
.canh-bao{{background:#fef9c3;border:1px solid #fde047;border-radius:10px;padding:14px;font-size:14px;margin-top:24px}}
.moi{{background:#fee2e2;color:#991b1b}}
img{{max-width:100%;border-radius:8px;border:1px solid #e2e8f0;margin-top:8px}}
</style></head><body><div class="bao">
<h1>🤖 Báo cáo phân tích lỗi kiểm thử</h1>
<div class="ngay">Sinh lúc {datetime.now():%H:%M %d/%m/%Y}</div>
<div class="trang-thai">{'✅ Tất cả đều đạt' if dat_het else f'❌ {tom_tat["hong"]} ca thất bại'}</div>
<div class="the"><div class="so-lieu">
  <div class="o"><b>{tom_tat['tong']}</b>Tổng ca</div>
  <div class="o"><b style="color:#059669">{tom_tat['dat']}</b>Đạt</div>
  <div class="o"><b style="color:#dc2626">{tom_tat['hong']}</b>Thất bại</div>
  <div class="o"><b>{tom_tat['bo_qua']}</b>Bỏ qua</div>
  <div class="o"><b>{tom_tat['thoi_gian']}s</b>Thời gian</div>
</div></div>"""]

    if xu_huong.get("co_lan_truoc"):
        c = xu_huong["chenh_lech_hong"]
        mo_ta = (f'🔺 Tăng thêm {c} ca thất bại' if c > 0
                 else f'🔻 Giảm {abs(c)} ca thất bại' if c < 0 else '➡️ Không đổi')
        h.append(f"""<div class="the"><h2 style="font-size:18px;margin-top:0">📈 So với lần chạy trước</h2>
<p style="font-size:14px;color:#64748b">Lần trước: {e(str(xu_huong.get('thoi_diem_truoc','—')))}</p>
<p><b>{mo_ta}</b></p><ul style="font-size:14px">
<li>🆕 {len(xu_huong['loi_moi'])} lỗi mới xuất hiện</li>
<li>✅ {len(xu_huong['loi_da_sua'])} lỗi đã hết</li>
<li>⏳ {len(xu_huong['loi_con_ton'])} lỗi vẫn còn</li></ul></div>""")

    if ket_qua_ai is not None:
        h.append(f'<div class="the"><h2 style="font-size:18px;margin-top:0">🧠 Nhận định chung</h2>'
                 f'<p>{e(ket_qua_ai.nhan_dinh_chung)}</p></div>')
    elif cac_nhom:
        h.append('<div class="canh-bao">⚠️ <b>Chưa bật phân tích AI.</b> Đặt biến môi trường '
                 '<code>ANTHROPIC_API_KEY</code> để có thêm phần phân tích nguyên nhân.</div>')

    for i, nhom in enumerate(cac_nhom, 1):
        p = ai.get(nhom["van_tay"])
        tieu_de = p.tieu_de if p else nhom["thong_diep"][:90]
        la_moi = nhom["van_tay"] in xu_huong.get("loi_moi", [])
        h.append(f'<div class="the"><h2 style="font-size:17px;margin-top:0">{i}. {e(tieu_de)}'
                 + ('<span class="nhan moi" style="margin-left:8px">MỚI</span>' if la_moi else '')
                 + '</h2>')
        h.append(f'<p style="font-size:13px;color:#64748b"><code>{e(nhom["loai_loi"])}</code> · '
                 f'<b>{nhom["so_luong"]} ca</b> · tầng: {e(", ".join(nhom["cac_tang"]))}</p>')
        if p:
            chu, nen = MAU_MUC_DO.get(p.muc_do, ("#334155", "#f1f5f9"))
            h.append(f'<table><tr><th>Mức độ</th><td><span class="nhan" '
                     f'style="background:{nen};color:{chu}">{e(p.muc_do)}</span></td></tr>'
                     f'<tr><th>Lỗi nằm ở</th><td>{e(p.loi_o_dau)}</td></tr>'
                     f'<tr><th>Độ tin cậy</th><td>{e(p.do_tin_cay)}</td></tr></table>')
            h.append(f'<p><b>Giả thuyết nguyên nhân (AI đề xuất):</b> {e(p.nguyen_nhan)}</p>')
            h.append(f'<p><b>Hướng sửa:</b> {e(p.huong_sua)}</p>')
            if p.tep_can_xem:
                h.append('<p><b>Nên xem:</b> ' + ", ".join(f'<code>{e(t)}</code>' for t in p.tep_can_xem) + '</p>')
        h.append('<details><summary>Traceback gốc và các ca thất bại</summary><ul style="font-size:13px">')
        for ca in nhom["cac_ca"]:
            h.append(f'<li><code>{e(ca["ma"])}</code>'
                     + (f' — 📸 {e(ca["anh_chup"])}' if ca["anh_chup"] else '') + '</li>')
        h.append('</ul><pre>' + e(nhom["cac_ca"][0]["traceback"][-2500:]) + '</pre>')
        anh = next((c["anh_chup"] for c in nhom["cac_ca"] if c["anh_chup"]), None)
        if anh:
            h.append(f'<img src="../{e(anh)}" alt="Ảnh màn hình lúc test gãy">')
        h.append('</details></div>')

    h.append('<div class="canh-bao">⚠️ <b>Lưu ý khi đọc báo cáo:</b> phần <i>Giả thuyết nguyên nhân</i> '
             'và <i>Hướng sửa</i> do AI suy luận từ traceback nên <b>có thể sai</b>. Luôn đối chiếu '
             'traceback gốc trước khi sửa code. Log đã được lọc bỏ mật khẩu, khoá API và đường dẫn '
             'cá nhân trước khi gửi đi phân tích.</div>')
    h.append('</div></body></html>')
    return "\n".join(h)


def ghi_bao_cao(thu_muc: Path, tom_tat, cac_nhom, ket_qua_ai, xu_huong) -> dict[str, Path]:
    thu_muc.mkdir(parents=True, exist_ok=True)
    md = thu_muc / "bao-cao-loi.md"
    ht = thu_muc / "bao-cao-loi.html"
    md.write_text(dung_markdown(tom_tat, cac_nhom, ket_qua_ai, xu_huong), encoding="utf-8")
    ht.write_text(dung_html(tom_tat, cac_nhom, ket_qua_ai, xu_huong), encoding="utf-8")
    return {"markdown": md, "html": ht}
