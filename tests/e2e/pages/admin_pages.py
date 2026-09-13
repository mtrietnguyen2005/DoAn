import re

from playwright.sync_api import expect

from .base_page import BasePage


class AdminLoginPage(BasePage):
    path = "/admin/"

    def login(self, username: str, password: str):
        self.page.fill("input[name='username']", username)
        self.page.fill("input[name='password']", password)
        self.page.click("input[type='submit'], button[type='submit']")
        return AdminDashboardPage(self.page, self.base_url)


class AdminDashboardPage(BasePage):
    path = "/admin/"

    def expect_loaded(self):
        expect(self.page).to_have_url(re.compile(r"/admin/$"))
        expect(self.page.get_by_text("Đơn hàng gần đây")).to_be_visible()
        return self

    def stat_value(self, title: str) -> int:
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
        self.page.click("button[name='_save'], input[name='_save']")
        return self

    def _select_autocomplete(self, field: str, term: str):
        select = self.page.locator(f"select[name='{field}']")
        if not select.get_attribute("data-ajax--url"):
            select.select_option(label=term)
            return

        self.page.click(f"select[name='{field}'] + span.select2")
        self.page.locator("input.select2-search__field").fill(term)

        option = self.page.locator("li.select2-results__option", has_text=term).first
        expect(option).to_be_visible()
        option.click()

        expect(self.page.locator(f"#select2-id_{field}-container")).to_contain_text(term)

    def row_count(self) -> int:
        return self.page.locator("#result_list tbody tr").count()

    def find_row(self, batch_code: str):
        return self.page.locator("#result_list tbody tr", has_text=batch_code)

    def success_message(self) -> str:
        box = self.page.locator("ul.messagelist li, div[class*='bg-green']").first
        return box.inner_text().strip() if box.count() else ""


class AdminOrderPage(BasePage):

    path = "/admin/orders/order/"

    def open_order(self, code: str):
        self.page.click(f"#result_list a:has-text('{code}')")
        return self

    def current_status(self) -> str:
        return self.page.locator("select[name='status']").input_value()

    def change_status(self, value: str):
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
