import pytest

from tests.e2e.pages import ShopPage


@pytest.fixture
def shop(page, api_url):
    return ShopPage(page, api_url).open()


@pytest.fixture
def logged_in(shop, factory):
    return shop.login(**factory.user())
