"""Page Object cho danh sách và chi tiết sản phẩm."""
from playwright.sync_api import expect

from .base_page import BasePage


class ProductListPage(BasePage):
    path = "/san-pham/"

    # ---- Bộ lọc ----
    def search(self, keyword: str):
        """Tìm kiếm bằng ô tìm kiếm trên thanh điều hướng.

        Giới hạn vào ``header`` vì form lọc bên dưới cũng có một ô ẩn cùng tên.
        """
        box = "header input[name='q']"
        self.page.fill(box, keyword)
        self.page.press(box, "Enter")
        return self

    def filter_by_category(self, slug: str):
        self.page.select_option("#filter-form select[name='category']", slug)
        return self._apply_filters()

    def filter_by_brand(self, slug: str):
        self.page.check(f"#filter-form input[name='brand'][value='{slug}']")
        return self._apply_filters()

    def filter_in_stock_only(self):
        self.page.check("#filter-form input[name='in_stock']")
        return self._apply_filters()

    def filter_on_sale_only(self):
        self.page.check("#filter-form input[name='on_sale']")
        return self._apply_filters()

    def filter_price(self, min_price=None, max_price=None):
        if min_price is not None:
            self.page.fill("#filter-form input[name='min_price']", str(min_price))
        if max_price is not None:
            self.page.fill("#filter-form input[name='max_price']", str(max_price))
        return self._apply_filters()

    def _apply_filters(self):
        """Bấm nút "Áp dụng bộ lọc" thay vì dựa vào sự kiện ``change`` của HTMX.

        Cách này chạy đúng trong cả hai trường hợp: có HTMX (nút kích hoạt
        ``hx-get``) và không có HTMX (form gửi theo cách thông thường).
        """
        self.page.click("#filter-form button[type='submit']")
        self._wait_for_grid()
        return self

    def sort_by(self, value: str):
        self.page.select_option("select[name='sort']", value)
        self._wait_for_grid()
        return self

    def _wait_for_grid(self):
        """Chờ lưới sản phẩm sẵn sàng.

        Không dùng ``networkidle`` vì trang nạp phông chữ và CSS từ CDN bên
        ngoài — nếu mạng chậm hoặc CDN bị chặn thì sẽ chờ vô tận. Thay vào đó
        chỉ chờ đúng phần tử cần dùng; các khẳng định ``expect_*`` bên dưới
        vốn đã tự thử lại nên không cần chờ thêm.
        """
        expect(self.page.locator("#product-results")).to_be_visible()

    # ---- Đọc kết quả ----
    @property
    def product_cards(self):
        return self.page.locator("#product-results article")

    def product_count(self) -> int:
        return self.product_cards.count()

    def product_names(self) -> list[str]:
        return [t.strip() for t in self.product_cards.locator("h3 a").all_inner_texts()]

    def result_summary(self) -> str:
        return self.page.locator("#product-results p").first.inner_text()

    def open_product(self, name: str):
        self.page.click(f"#product-results a:has-text('{name}')")
        return ProductDetailPage(self.page, self.base_url)

    def add_first_product_to_cart(self):
        """Thêm sản phẩm đầu tiên CÒN HÀNG vào giỏ.

        Bỏ qua các nút bị vô hiệu hoá: sản phẩm hết hàng có nút ``disabled``,
        bấm vào sẽ chờ mãi tới khi hết thời gian.
        """
        self.page.locator("#product-results button[data-add-to-cart]:not([disabled])") \
            .first.click()
        expect(self.cart_badge).to_be_visible()
        return self

    def add_product_to_cart(self, name: str):
        """Thêm đúng sản phẩm theo tên."""
        card = self.product_cards.filter(has_text=name).first
        card.locator("button[data-add-to-cart]").click()
        expect(self.cart_badge).to_be_visible()
        return self

    def expect_product_count(self, count: int):
        """Khẳng định số sản phẩm hiển thị. Playwright tự thử lại tới khi khớp."""
        expect(self.product_cards).to_have_count(count)
        return self

    def expect_product_names(self, names: list[str]):
        expect(self.product_cards.locator("h3 a")).to_have_text(names)
        return self

    def expect_empty_result(self):
        expect(self.page.get_by_text("Không tìm thấy sản phẩm nào")).to_be_visible()
        return self


class ProductDetailPage(BasePage):
    def __init__(self, page, base_url, slug: str = None):
        super().__init__(page, base_url)
        if slug:
            self.path = f"/san-pham/{slug}/"

    @property
    def title(self) -> str:
        return self.page.locator("h1").inner_text().strip()

    @property
    def price_text(self) -> str:
        return self.page.locator("div.text-3xl.font-extrabold").first.inner_text().strip()

    def stock_text(self) -> str:
        return self.page.locator("dl").first.inner_text()

    def set_quantity(self, quantity: int):
        self.page.fill("#qty", str(quantity))
        return self

    def add_to_cart(self):
        self.page.click("button[data-add-to-cart]")
        # Nút bấm gọi fetch() rồi cập nhật số trên biểu tượng giỏ hàng.
        # Không chờ "networkidle" (trang còn tải CSS/phông từ CDN) mà chờ đúng
        # dấu hiệu cần: số trên giỏ hàng hiện ra.
        expect(self.cart_badge).to_be_visible()
        return self

    # ---- Đánh giá ----
    def write_review(self, rating: int, content: str, title: str = ""):
        self.page.select_option("select[name='rating']", str(rating))
        if title:
            self.page.fill("input[name='title']", title)
        self.page.fill("textarea[name='content']", content)
        self.page.click("form[action*='danh-gia'] button[type='submit']")
        return self

    def my_review_text(self) -> str:
        box = self.page.locator("div.bg-brand-50").first
        return box.inner_text() if box.count() else ""

    def expect_my_review_contains(self, fragment: str):
        """Khẳng định khối "Đánh giá của bạn" chứa nội dung cho trước."""
        expect(self.page.locator("div.bg-brand-50").first).to_contain_text(fragment)
        return self

    def expect_no_my_review(self):
        expect(self.page.locator("div.bg-brand-50")).to_have_count(0)
        return self

    def edit_my_review(self):
        self.page.click("a:has-text('Sửa')")
        return self

    def delete_my_review(self):
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.click("button:has-text('Xóa')")
        return self

    def review_count_text(self) -> str:
        return self.page.locator("section h2:has-text('Đánh giá sản phẩm')").inner_text()
