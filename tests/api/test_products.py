import pytest


def test_req01_list_returns_all_products(api, factory):
    assert len(api.get("/api/products").json()) == len(factory.products)


@pytest.mark.parametrize("field", ["id", "name", "price", "stock"])
def test_req01_product_has_field(api, field):
    assert all(field in p for p in api.get("/api/products").json())


@pytest.mark.parametrize("pid", [1, 2, 3, 4, 5])
def test_req01_get_product_by_id(api, factory, pid):
    assert api.get(f"/api/products/{pid}").json() == factory.product(pid=pid)


def test_req01_unknown_product_404(api):
    assert api.get("/api/products/999").status_code == 404
