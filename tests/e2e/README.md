# Giai đoạn 2 — E2E Test bằng Playwright

Thư mục này sẽ chứa:

```
tests/e2e/
├── conftest.py              # fixture trình duyệt, live server, tự chụp ảnh khi test gãy
├── pages/                   # Page Object Model
│   ├── base_page.py
│   ├── login_page.py
│   ├── register_page.py
│   ├── product_list_page.py
│   ├── product_detail_page.py
│   ├── cart_page.py
│   ├── checkout_page.py
│   ├── order_list_page.py
│   ├── order_detail_page.py
│   └── admin/
│       ├── admin_login_page.py
│       ├── batch_page.py
│       ├── order_admin_page.py
│       └── dashboard_page.py
├── test_customer_flow.py    # Đăng ký → Đăng nhập → Lọc → Giỏ hàng → Đặt hàng → Huỷ đơn
└── test_admin_flow.py       # Đăng nhập admin → Thêm lô → Duyệt đơn → Kiểm tra Dashboard
```

Chưa được cài đặt. Chạy Giai đoạn 2 để sinh các tệp này.
