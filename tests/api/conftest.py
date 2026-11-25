import pytest

from tests.api.client import Api


@pytest.fixture
def api(api_url):
    return Api(api_url)


@pytest.fixture
def shopper(api, factory):
    assert api.login(**factory.user()).status_code == 200
    return api
