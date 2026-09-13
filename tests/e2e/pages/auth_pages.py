from playwright.sync_api import expect

from .base_page import BasePage

MAIN_FORM = "form[method='post']"


class RegisterPage(BasePage):
    path = "/tai-khoan/dang-ky/"

    def register(self, *, username, email, password, last_name="Nguyễn", first_name="Test", phone=""):
        self.page.fill(f"{MAIN_FORM} input[name='username']", username)
        self.page.fill("input[name='last_name']", last_name)
        self.page.fill("input[name='first_name']", first_name)
        self.page.fill("input[name='email']", email)
        if phone:
            self.page.fill("input[name='phone']", phone)
        self.page.fill("input[name='password1']", password)
        self.page.fill("input[name='password2']", password)
        self.page.click(f"{MAIN_FORM} button[type='submit']")
        return self

    def field_errors(self) -> list[str]:
        return [t.strip() for t in self.page.locator("p.text-rose-600").all_inner_texts()]

    def expect_field_error(self, fragment: str):
        expect(self.page.locator("p.text-rose-600").filter(has_text=fragment).first) \
            .to_be_visible()
        return self


class LoginPage(BasePage):
    path = "/tai-khoan/dang-nhap/"

    def login(self, username: str, password: str, remember: bool = True):
        self.page.fill(f"{MAIN_FORM} input[name='username']", username)
        self.page.fill(f"{MAIN_FORM} input[name='password']", password)
        checkbox = self.page.locator("input[name='remember_me']")
        if checkbox.count():
            if remember and not checkbox.is_checked():
                checkbox.check()
            elif not remember and checkbox.is_checked():
                checkbox.uncheck()
        self.page.click(f"{MAIN_FORM} button[type='submit']")
        return self

    def error_message(self) -> str:
        box = self.page.locator("div.bg-rose-50").first
        return box.inner_text().strip() if box.count() else ""

    def expect_error(self, fragment: str):
        expect(self.page.locator("div.bg-rose-50").first).to_contain_text(fragment)
        return self

    def expect_logged_in(self):
        expect(self.page.locator("a[href='/tai-khoan/dang-nhap/']")).to_have_count(0)
        return self
