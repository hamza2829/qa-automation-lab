import os

import pytest
import requests

from tests.factory import DataFactory


@pytest.fixture(scope="session")
def api_url():
    return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(autouse=True)
def reset_shop(api_url):
    requests.post(f"{api_url}/api/reset", timeout=10).raise_for_status()


@pytest.fixture
def factory():
    return DataFactory()
