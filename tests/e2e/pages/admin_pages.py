"""Page Object cho trang quản trị (/admin, giao diện django-unfold)."""
import re

from playwright.sync_api import expect

from .base_page import BasePage


class AdminLoginPage(BasePage):
    #: Vào thẳng /admin/ rồi để Django tự chuyển hướng sang trang đăng nhập kèm
    #: tham số ``next``. Nếu mở trực tiếp /admin/login/ mà không có ``next``,
    #: Django Admin sẽ chuyển hướng theo ``LOGIN_REDIRECT_URL`` (trang chủ cửa
    #: hàng) sau khi đăng nhập, không phải về dashboard.
    path = "/admin/"

    def login(self, username: str, password: str):
        self.page.fill("input[name='username']", username)
        self.page.fill("input[name='password']", password)
        self.page.click("input[type='submit'], button[type='submit']")
        return AdminDashboardPage(self.page, self.base_url)


class AdminDashboardPage(BasePage):
    path = "/admin/"

    def expect_loaded(self):
        """Khẳng định đang đứng ở trang Dashboard của Admin."""
        expect(self.page).to_have_url(re.compile(r"/admin/$"))
        expect(self.page.get_by_text("Đơn hàng gần đây")).to_be_visible()
        return self

    # ---- Thẻ thống kê ----
    def stat_value(self, title: str) -> int:
        """Đọc con số của một thẻ thống kê, ví dụ stat_value('Đơn hàng')."""
        card = self.page.locator("div", has_text=title).filter(
            has=self.page.locator("p.text-3xl")).last
        return int(card.locator("p.text-3xl").inner_text().replace(",", "").replace(".", "").strip())

    def order_status_count(self, label: str) -> int:
        row = self.page.locator("div.flex.items-center.justify-between", has_text=label).first
        return int(row.locator("span").last.inner_text().strip())

    def revenue_text(self) -> str:
        return self.page.locator("p.text-emerald-600").first.inner_text().strip()

    def profit_text(self) -> str:
        return self.page.locator("p.text-blue-600").first.inner_text().strip()

    def low_stock_skus(self) -> list[str]:
        return [t.strip() for t in self.page.locator(
            "h3:has-text('tồn kho') >> xpath=../.. >> tbody a").all_inner_texts()]


class AdminBatchPage(BasePage):
    """Quản lý lô hàng: /admin/inventory/batch/"""

    path = "/admin/inventory/batch/"
    add_path = "/admin/inventory/batch/add/"

    def go_add(self):
        return self.go(self.add_path)

    def create_batch(self, *, batch_code, product_sku, quantity, cost_price,
                     received_date):
        self.page.fill("input[name='batch_code']", batch_code)
        self._select_autocomplete("product", product_sku)
        self.page.fill("input[name='quantity_in']", str(quantity))
        self.page.fill("input[name='cost_price']", str(cost_price))
        self.page.fill("input[name='received_date']", received_date)
        self.save()
        return self

    def save(self):
        """Bấm nút Lưu. django-unfold dùng <button>, Django Admin gốc dùng <input>."""
        self.page.click("button[name='_save'], input[name='_save']")
        return self

    def _select_autocomplete(self, field: str, term: str):
        """Chọn giá trị trong ô autocomplete (select2) của Django Admin.

        ``term`` phải là từ khoá thật sự khớp với ``search_fields`` của
        ModelAdmin — ví dụ mã SKU. Không dùng ``str(obj)`` vì Django Admin tách
        từ khoá theo dấu cách và yêu cầu MỌI từ đều khớp; chuỗi dạng
        ``[CPU0001] Intel Core i5`` sẽ không tìm ra gì.
        """
        select = self.page.locator(f"select[name='{field}']")
        if not select.get_attribute("data-ajax--url"):
            select.select_option(label=term)
            return

        # select2 chèn một <span class="select2"> ngay sau thẻ <select> gốc
        self.page.click(f"select[name='{field}'] + span.select2")
        self.page.locator("input.select2-search__field").fill(term)

        option = self.page.locator("li.select2-results__option", has_text=term).first
        expect(option).to_be_visible()
        option.click()

        # Khẳng định giá trị đã thực sự được gán, để lỗi lộ ra ngay tại đây
        # thay vì biến thành lỗi khó hiểu ở bước lưu form. Phải trỏ đúng id của
        # trường: form này có nhiều ô autocomplete (sản phẩm, nhà cung cấp) nên
        # selector chung sẽ khớp nhầm.
        expect(self.page.locator(f"#select2-id_{field}-container")).to_contain_text(term)

    def row_count(self) -> int:
        return self.page.locator("#result_list tbody tr").count()

    def find_row(self, batch_code: str):
        return self.page.locator("#result_list tbody tr", has_text=batch_code)

    def success_message(self) -> str:
        box = self.page.locator("ul.messagelist li, div[class*='bg-green']").first
        return box.inner_text().strip() if box.count() else ""


class AdminOrderPage(BasePage):
    """Quản lý đơn hàng: /admin/orders/order/"""

    path = "/admin/orders/order/"

    def open_order(self, code: str):
        self.page.click(f"#result_list a:has-text('{code}')")
        return self

    def current_status(self) -> str:
        return self.page.locator("select[name='status']").input_value()

    def change_status(self, value: str):
        """Đổi trạng thái đơn rồi lưu (đi qua service nên có ghi lịch sử)."""
        self.page.select_option("select[name='status']", value)
        self.page.click("button[name='_save'], input[name='_save']")
        return self

    def status_history_rows(self) -> int:
        return self.page.locator("[id^='status_history-'] tr.form-row, "
                                 "#status_history-group tbody tr").count()

    def select_all_and_apply(self, action: str):
        self.page.check("#action-toggle")
        self.page.select_option("select[name='action']", action)
        self.page.click("button[type='submit'][name='index'], button.button[title='Run the selected action']")
        return self

    def messages(self) -> list[str]:
        return [t.strip() for t in self.page.locator("ul.messagelist li").all_inner_texts()]
