def _fill(shopper, factory, *items):
    for pid, qty in items:
        shopper.post("/api/cart/items", json=factory.item(factory.product(pid=pid), qty))


def test_req04_order_total_matches_cart(shopper, factory):
    _fill(shopper, factory, (1, 1), (2, 2))
    total = shopper.get("/api/cart").json()["total"]
    assert shopper.post("/api/orders", json={}).json()["total"] == total


def test_req04_discount_applied(shopper, factory):
    _fill(shopper, factory, (3, 1))
    r = shopper.post("/api/orders", json={"discount_code": "SAVE10"})
    assert r.json()["total"] == round(49.9 * 0.9, 2)


def test_req04_invalid_discount_rejected(shopper, factory):
    _fill(shopper, factory, (3, 1))
    assert shopper.post("/api/orders", json={"discount_code": "FREE"}).status_code == 400


def test_req04_empty_cart_rejected(shopper):
    assert shopper.post("/api/orders", json={}).status_code == 400


def test_req04_order_reduces_stock(shopper, factory):
    _fill(shopper, factory, (2, 3))
    shopper.post("/api/orders", json={})
    assert shopper.get("/api/products/2").json()["stock"] == 97


def test_req04_cart_empty_after_order(shopper, factory):
    _fill(shopper, factory, (1, 1))
    shopper.post("/api/orders", json={})
    assert shopper.get("/api/cart").json()["items"] == []


def test_req04_get_own_order(shopper, factory):
    _fill(shopper, factory, (1, 1))
    oid = shopper.post("/api/orders", json={}).json()["id"]
    assert shopper.get(f"/api/orders/{oid}").json()["user"] == "alice"
