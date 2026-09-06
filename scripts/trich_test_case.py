# -*- coding: utf-8 -*-
"""Sinh file Excel danh mục test case từ mã nguồn thật.

Tự chạy ``pytest --collect-only`` để lấy danh sách ca thật (kể cả parametrize),
không cần bước tạo ``nodes.txt`` thủ công — script này và
``sinh_excel_test_case.py`` phải dùng chung một tệp trung gian nên đường dẫn
được tính tương đối theo thư mục ``scripts/``, chạy được trên mọi máy.
"""
import ast, pathlib, re, subprocess, sys, collections

GOC = pathlib.Path(__file__).resolve().parent.parent
NODES = GOC / 'scripts' / '_nodes.txt'
RONG_PKL = GOC / 'scripts' / '_rows.pkl'

ket_qua = subprocess.run(
    [sys.executable, '-m', 'pytest', '--collect-only', '-q', '--tat-ca'],
    cwd=GOC, capture_output=True, text=True, check=True,
)
NODES.write_text(
    '\n'.join(d for d in ket_qua.stdout.splitlines() if '::' in d), encoding='utf-8'
)

TANG = {'unit': 'Unit', 'integration': 'Integration', 'e2e': 'E2E'}

# Giải nghĩa fixture để cột mô tả dễ đọc
FIXTURE = {
    'db': 'kết nối database sạch', 'transactional_db': 'database ghi thật (cho E2E)',
    'client': 'Django test client (giả lập trình duyệt qua HTTP)',
    'page': 'tab trình duyệt Chromium', 'site_url': 'địa chỉ web server test',
    'settings': 'ghi đè cấu hình Django', 'tmp_path': 'thư mục tạm',
    'customer': 'khách hàng có sẵn (khachhang)', 'other_customer': 'khách hàng thứ hai',
    'staff_user': 'admin thường (is_staff, đủ permission Django)',
    'superuser': 'superuser toàn quyền', 'address': 'địa chỉ nhận hàng của khách',
    'category': 'danh mục CPU', 'brand': 'thương hiệu Intel', 'supplier': 'nhà cung cấp',
    'product': 'sản phẩm 1.500.000đ, CHƯA có lô hàng (tồn 0)',
    'discounted_product': 'sản phẩm 8tr giảm còn 7tr',
    'product_factory': 'hàm tạo sản phẩm tuỳ ý', 'batch_factory': 'hàm tạo lô hàng tuỳ ý',
    'user_factory': 'hàm tạo người dùng tuỳ ý', 'order_factory': 'hàm tạo đơn hàng thật',
    'cart_factory': 'hàm tạo giỏ hàng giả lập',
    'batch_early': 'lô LO-SOM: hạn 10 ngày, 4 SP, giá vốn 1.000.000đ',
    'batch_late': 'lô LO-MUON: hạn 200 ngày, 10 SP, giá vốn 1.200.000đ',
    'product_with_batches': 'sản phẩm có 2 lô, tổng tồn kho 14',
    'promo_percent': 'mã GIAM10 (giảm 10%, tối đa 500k)',
    'promo_fixed': 'mã GIAM200K (giảm 200k, đơn từ 5tr)',
    'promo_expired': 'mã đã hết hạn', 'order': 'đơn hàng 2 SP lấy từ lô sớm',
    'review': 'đánh giá 5 sao có sẵn', 'today': 'ngày hôm nay',
    'shop_data': 'cửa hàng mẫu E2E (3 SP, 3 lô, 1 mã giảm giá)',
    'customer_account': 'tài khoản khách để đăng nhập E2E',
    'admin_account': 'tài khoản quản trị để đăng nhập E2E',
    'logged_in_customer': 'khách ĐÃ đăng nhập sẵn qua giao diện',
    'logged_in_admin': 'admin ĐÃ đăng nhập sẵn vào /admin',
    'catalog': '2 sản phẩm: một còn hàng, một hết hàng',
    'product_ban': 'sản phẩm 5tr giảm còn 4,5tr, tồn 5',
    'dashboard_request': 'request giả lập vào /admin/',
    'du_lieu_dashboard': 'dữ liệu cho dashboard (đơn hàng, lô sắp hết hạn)',
    'nhan_vien': 'admin thường dùng cho test phân quyền',
    'model': 'model đang xét (chạy lặp)', 'url': 'đường dẫn đang xét (chạy lặp)',
}

def viet_hoa_ten(ten):
    s = ten.replace('test_', '').replace('_', ' ').strip()
    return s[0].upper() + s[1:] if s else s

def mo_ta_buoc(node, nguon):
    """Chuyển thân hàm test thành các bước thực thi đọc được."""
    buoc, ky_vong = [], []
    for stmt in node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            continue                                   # bỏ docstring
        try:
            code = ast.get_source_segment(nguon, stmt) or ''
        except Exception:
            code = ''
        code = ' '.join(code.split())
        if not code:
            continue
        if isinstance(stmt, ast.Assert):
            ky_vong.append(code.replace('assert ', ''))
        elif isinstance(stmt, ast.With) and 'raises' in code:
            m = re.search(r'raises\((\w+)', code)
            ky_vong.append(f'Ném ngoại lệ {m.group(1)}' if m else code)
        elif 'expect(' in code or '.expect_' in code:
            ky_vong.append(code)
        elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
            continue
        else:
            buoc.append(code)
    return buoc, ky_vong

# ---- Đếm số ca thật từ pytest ----
dem_lop = collections.Counter()
for dong in open(NODES):
    p = dong.strip().split('::')
    if len(p) >= 3:
        dem_lop[(p[0], p[1])] += 1

hang = []
stt = 0
for thu_muc in ('unit', 'integration', 'e2e'):
    d = pathlib.Path('tests') / thu_muc
    for tep in sorted(d.rglob('test_*.py')):
        nguon = tep.read_text(encoding='utf-8')
        cay = ast.parse(nguon)
        for lop in [n for n in cay.body if isinstance(n, ast.ClassDef)]:
            mo_ta_lop = ast.get_docstring(lop) or ''
            mo_ta_lop = ' '.join(mo_ta_lop.split())
            for f in [x for x in lop.body if isinstance(x, ast.FunctionDef) and x.name.startswith('test_')]:
                stt += 1
                doc = ast.get_docstring(f) or ''
                doc = ' '.join(doc.split())
                fixtures = [a.arg for a in f.args.args if a.arg != 'self']
                lap = [ast.unparse(dc) for dc in f.decorator_list if 'parametrize' in ast.unparse(dc)]
                buoc, ky_vong = mo_ta_buoc(f, nguon)

                phan = []
                phan.append('【Ý NGHĨA】')
                phan.append(doc if doc else viet_hoa_ten(f.name) + '.')
                if mo_ta_lop:
                    phan.append(f'(Nhóm: {mo_ta_lop})')
                phan.append('')
                if fixtures:
                    phan.append('【DỮ LIỆU CHUẨN BỊ】')
                    for fx in fixtures:
                        phan.append(f'  • {fx}: {FIXTURE.get(fx, "—")}')
                    phan.append('')
                if lap:
                    phan.append('【CHẠY LẶP NHIỀU BỘ DỮ LIỆU】')
                    phan.append('  ' + lap[0][:200])
                    phan.append('')
                if buoc:
                    phan.append('【CÁC BƯỚC THỰC THI】')
                    for i, b in enumerate(buoc, 1):
                        phan.append(f'  {i}. {b[:300]}')
                    phan.append('')
                if ky_vong:
                    phan.append('【KẾT QUẢ MONG ĐỢI】')
                    for k in ky_vong:
                        phan.append(f'  ✓ {k[:300]}')

                hang.append({
                    'STT': stt,
                    'Tầng': TANG[thu_muc],
                    'Tệp': tep.name,
                    'Nhóm chức năng': lop.name,
                    'Tên test case': f.name,
                    'Ý nghĩa và cách thực thi': '\n'.join(phan),
                    '_so_ca': dem_lop[(str(tep).replace('\\', '/'), lop.name)],
                })

print(f'Đã trích {len(hang)} hàm test')
import pickle
pickle.dump(hang, open(RONG_PKL, 'wb'))
