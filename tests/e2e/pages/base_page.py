"""Lớp cơ sở cho toàn bộ Page Object.

Mọi trang đều kế thừa lớp này để dùng chung các thao tác điều hướng và
tiện ích. Playwright có sẵn cơ chế **auto-waiting**: mỗi hành động
(``click``, ``fill``…) tự chờ phần tử xuất hiện, hiện hình, ổn định và
nhận được tương tác rồi mới thực hiện — nên trong toàn bộ bộ test này
không có chỗ nào phải viết ``sleep``.
"""
import re

from playwright.sync_api import Page, expect


class BasePage:
    #: Đường dẫn tương đối của trang, lớp con ghi đè
    path: str = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # ---- Điều hướng ----
    def url_for(self, path: str = None) -> str:
        return f"{self.base_url}{path if path is not None else self.path}"

    def go(self, path: str = None):
        """Mở trang và chờ DOM sẵn sàng."""
        self.page.goto(self.url_for(path), wait_until="domcontentloaded")
        return self

    # ---- Thành phần dùng chung trên mọi trang ----
    @property
    def cart_badge(self):
        return self.page.locator("#cart-badge")

    def cart_count(self) -> int:
        """Số sản phẩm đang hiển thị trên biểu tượng giỏ hàng."""
        badge = self.cart_badge
        if badge.is_hidden():
            return 0
        text = (badge.inner_text() or "").strip()
        return int(text) if text.isdigit() else 0

    def open_cart(self):
        self.page.click("a[href='/gio-hang/']")

    def flash_messages(self) -> list[str]:
        """Danh sách thông báo (success / error / warning) đang hiển thị."""
        return [t.strip() for t in self.page.locator("main ~ div span, .max-w-7xl > div span").all_inner_texts()]

    # ---- Tiện ích khẳng định ----
    def expect_url_contains(self, fragment: str):
        """Khẳng định URL hiện tại có chứa đoạn cho trước.

        Lưu ý: ``to_have_url`` của Playwright bản Python chỉ nhận chuỗi hoặc
        biểu thức chính quy — không nhận hàm lambda như bản JavaScript.
        """
        expect(self.page).to_have_url(re.compile(re.escape(fragment)))
        return self

    def expect_text_visible(self, text: str):
        expect(self.page.get_by_text(text, exact=False).first).to_be_visible()
        return self

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)
