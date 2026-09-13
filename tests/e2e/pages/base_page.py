import re

from playwright.sync_api import Page, expect


class BasePage:
    path: str = "/"

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    def url_for(self, path: str = None) -> str:
        return f"{self.base_url}{path if path is not None else self.path}"

    def go(self, path: str = None):
        self.page.goto(self.url_for(path), wait_until="domcontentloaded")
        return self

    @property
    def cart_badge(self):
        return self.page.locator("#cart-badge")

    def cart_count(self) -> int:
        badge = self.cart_badge
        if badge.is_hidden():
            return 0
        text = (badge.inner_text() or "").strip()
        return int(text) if text.isdigit() else 0

    def open_cart(self):
        self.page.click("a[href='/gio-hang/']")

    def flash_messages(self) -> list[str]:
        return [t.strip() for t in self.page.locator("main ~ div span, .max-w-7xl > div span").all_inner_texts()]

    def expect_url_contains(self, fragment: str):
        expect(self.page).to_have_url(re.compile(re.escape(fragment)))
        return self

    def expect_text_visible(self, text: str):
        expect(self.page.get_by_text(text, exact=False).first).to_be_visible()
        return self

    def screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)
