"""Page Object cho giỏ hàng và thanh toán."""
from playwright.sync_api import expect

from .base_page import BasePage
from .order_pages import OrderDetailPage


class CartPage(BasePage):
    path = "/gio-hang/"

    @property
    def line_items(self):
        return self.page.locator("#cart-items > div > div")

    def item_count(self) -> int:
        return self.line_items.count()

    def is_empty(self) -> bool:
        return self.page.get_by_text("Giỏ hàng đang trống").is_visible()

    def subtotal_text(self) -> str:
        return self.page.locator("dl div", has_text="Tạm tính").inner_text()

    def total_text(self) -> str:
        return self.page.locator("dt:has-text('Tổng cộng')").locator("xpath=..").inner_text()

    def increase_first_item(self):
        """Bấm dấu + trên dòng hàng đầu tiên (thao tác qua HTMX)."""
        self.line_items.first.locator("button:has-text('+')").click()
        return self

    def decrease_first_item(self):
        self.line_items.first.locator("button:has-text('−')").click()
        return self

    def first_item_quantity(self) -> int:
        text = self.line_items.first.locator("form span").first.inner_text().strip()
        return int(text) if text.isdigit() else 0

    def remove_first_item(self):
        self.line_items.first.locator("button:has-text('Xóa')").click()
        return self

    def expect_first_item_quantity(self, quantity: int):
        """Khẳng định số lượng dòng hàng đầu tiên, tự thử lại tới khi khớp."""
        expect(self.line_items.first.locator("form span").first).to_have_text(str(quantity))
        return self

    def expect_empty(self):
        expect(self.page.get_by_text("Giỏ hàng đang trống")).to_be_visible()
        return self

    def expect_item_count(self, count: int):
        expect(self.line_items).to_have_count(count)
        return self

    def apply_promo(self, code: str):
        self.page.fill("input[name='code']", code)
        self.page.click("button:has-text('Áp dụng')")
        return self

    def remove_promo(self):
        self.page.click("button:has-text('Gỡ mã')")
        return self

    def expect_discount_contains(self, fragment: str):
        """Chờ trang tải lại sau khi áp mã rồi khẳng định số tiền giảm."""
        expect(self.page.locator("dt", has_text="Giảm giá").locator("xpath=..")) \
            .to_contain_text(fragment)
        return self

    def expect_promo_error(self, fragment: str):
        expect(self.page.get_by_text(fragment, exact=False).first).to_be_visible()
        return self

    def discount_text(self) -> str:
        row = self.page.locator("dt:has-text('Giảm giá')")
        return row.locator("xpath=..").inner_text() if row.count() else ""

    def go_to_checkout(self):
        self.page.click("a:has-text('Tiến hành đặt hàng')")
        return CheckoutPage(self.page, self.base_url)


class CheckoutPage(BasePage):
    path = "/gio-hang/thanh-toan/"

    def fill_receiver(self, *, name, phone, province, district, ward, street, note=""):
        self.page.fill("input[name='receiver_name']", name)
        self.page.fill("input[name='receiver_phone']", phone)
        self.page.fill("input[name='province']", province)
        self.page.fill("input[name='district']", district)
        self.page.fill("input[name='ward']", ward)
        self.page.fill("input[name='street']", street)
        if note:
            self.page.fill("textarea[name='customer_note']", note)
        return self

    def use_saved_address(self, index: int = 0):
        self.page.locator("button.address-pick").nth(index).click()
        return self

    def total_text(self) -> str:
        return self.page.locator("dt:has-text('Tổng cộng')").locator("xpath=..").inner_text()

    def place_order(self):
        self.page.click("button:has-text('Đặt hàng ngay')")
        return OrderSuccessPage(self.page, self.base_url)

    def field_errors(self) -> list[str]:
        return [t.strip() for t in self.page.locator("p.text-rose-600").all_inner_texts()]


class OrderSuccessPage(BasePage):
    def expect_success(self):
        expect(self.page.get_by_role("heading", name="Đặt hàng thành công!")).to_be_visible()
        return self

    def order_code(self) -> str:
        return self.page.locator("p.text-brand-600").first.inner_text().strip()

    def total_text(self) -> str:
        return self.page.locator("p.text-rose-600").first.inner_text().strip()

    def view_order_detail(self):
        self.page.click("a:has-text('Xem chi tiết đơn hàng')")
        return OrderDetailPage(self.page, self.base_url)
