"""Page objects for the synthetic shop UI."""
import re

from playwright.sync_api import expect


class ShopPage:
    def __init__(self, page, url):
        self.page = page
        self.url = url
        self.login_msg = page.locator("#login-msg")
        self.products = page.locator(".product")
        self.cart_items = page.locator("#cart-items li")
        self.cart_total = page.locator("#cart-total")
        self.order_msg = page.locator("#order-msg")

    def open(self):
        self.page.goto(self.url)
        return self

    def login(self, username, password):
        self.page.fill("#username", username)
        self.page.fill("#password", password)
        self.page.click("#login-btn")
        expect(self.login_msg).to_have_text(re.compile(".+"))
        return self

    def add(self, pid, qty=1):
        self.page.fill(f"#qty-{pid}", str(qty))
        self.page.click(f"#add-{pid}")
        return self

    def checkout(self, code=""):
        self.page.fill("#discount", code)
        self.page.click("#checkout-btn")
        return self
