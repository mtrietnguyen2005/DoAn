"""Page Object cho lịch sử đơn hàng và chi tiết đơn."""
from playwright.sync_api import expect

from .base_page import BasePage


class OrderListPage(BasePage):
    path = "/gio-hang/don-hang/"

    @property
    def order_cards(self):
        return self.page.locator("div.bg-white.rounded-2xl.border").filter(has_text="DH")

    def order_codes(self) -> list[str]:
        return [t.strip() for t in self.page.locator("a[href*='/don-hang/DH']").all_inner_texts()]

    def filter_by_status(self, label: str):
        self.page.click(f"a:has-text('{label}')")
        return self

    def open_order(self, code: str):
        self.page.click(f"a:has-text('{code}')")
        return OrderDetailPage(self.page, self.base_url)

    def is_empty(self) -> bool:
        return self.page.get_by_text("Bạn chưa có đơn hàng nào").is_visible()


class OrderDetailPage(BasePage):
    def __init__(self, page, base_url, code: str = None):
        super().__init__(page, base_url)
        if code:
            self.path = f"/gio-hang/don-hang/{code}/"

    def order_code(self) -> str:
        return self.page.locator("h1").inner_text().replace("Đơn hàng", "").strip()

    @property
    def status_badge(self):
        """Nhãn trạng thái đơn.

        Giới hạn trong ``main`` vì badge số lượng giỏ hàng trên header cũng có
        lớp ``rounded-full`` và sẽ bị chọn nhầm nếu tìm trên toàn trang.
        """
        return self.page.locator("main span.rounded-full").first

    def status_text(self) -> str:
        return self.status_badge.inner_text().strip()

    def status_history(self) -> list[str]:
        return [t.strip() for t in self.page.locator("ol li p.font-semibold").all_inner_texts()]

    def item_names(self) -> list[str]:
        return [t.strip() for t in self.page.locator("h2:has-text('Sản phẩm đã đặt') ~ div p, "
                                                     "h2:has-text('Sản phẩm đã đặt') ~ div a").all_inner_texts()]

    def total_text(self) -> str:
        return self.page.locator("dt:has-text('Tổng cộng')").locator("xpath=..").inner_text()

    # ---- Huỷ đơn ----
    def can_cancel(self) -> bool:
        return self.page.locator("button:has-text('Xác nhận hủy đơn')").count() > 0

    def cancel_order(self, reason: str = "Đổi ý không mua nữa"):
        self.page.fill("textarea[name='reason']", reason)
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.click("button:has-text('Xác nhận hủy đơn')")
        return self

    def expect_cancelled(self):
        expect(self.status_badge).to_have_text("Đã hủy")
        return self

    def expect_status(self, label: str):
        expect(self.status_badge).to_have_text(label)
        return self

    def shipping_blocked_notice(self) -> bool:
        return self.page.get_by_text("đang được giao nên không thể hủy").count() > 0
