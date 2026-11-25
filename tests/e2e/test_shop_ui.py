from playwright.sync_api import expect


def test_req02_ui_login_success(shop, factory):
    expect(shop.login(**factory.user()).login_msg).to_have_text("Logged in as alice")


def test_req02_ui_login_wrong_password(shop, factory):
    expect(shop.login(**factory.user(valid=False)).login_msg).to_have_text("Login failed")


def test_req01_ui_shows_all_products(shop, factory):
    expect(shop.products).to_have_count(len(factory.products))


def test_req03_ui_add_to_cart(logged_in):
    expect(logged_in.add(1).cart_items).to_have_count(1)


def test_req03_ui_cart_total_with_quantity(logged_in):
    expect(logged_in.add(1, 2).cart_total).to_have_text("Total: 39.98")


def test_req04_ui_checkout(logged_in):
    expect(logged_in.add(2, 1).checkout().order_msg).to_contain_text("confirmed, total 2.50")
