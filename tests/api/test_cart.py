import pytest


def test_req03_add_item(shopper, factory):
    r = shopper.post("/api/cart/items", json=factory.item())
    assert r.status_code == 201 and len(r.json()["items"]) == 1


@pytest.mark.parametrize("qty", [1, 2, 5])
def test_req03_total_uses_quantity(shopper, factory, qty):
    p = factory.product(pid=1)
    cart = shopper.post("/api/cart/items", json=factory.item(p, qty)).json()
    assert cart["total"] == round(p["price"] * qty, 2)


@pytest.mark.parametrize("qty", [0, -1])
def test_req03_invalid_quantity_rejected(shopper, factory, qty):
    assert shopper.post("/api/cart/items", json=factory.item(quantity=qty)).status_code == 422


def test_req03_out_of_stock_rejected(shopper, factory):
    assert shopper.post("/api/cart/items", json=factory.item(factory.product(in_stock=False))).status_code == 409


def test_req03_quantity_above_stock_rejected(shopper, factory):
    p = factory.product(pid=5)
    assert shopper.post("/api/cart/items", json=factory.item(p, p["stock"] + 1)).status_code == 409


def test_req03_clear_cart(shopper, factory):
    shopper.post("/api/cart/items", json=factory.item())
    assert shopper.delete("/api/cart").json() == {"items": [], "total": 0}
