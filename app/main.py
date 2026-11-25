"""Synthetic web shop (FastAPI). All data is invented."""
import json
import secrets
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.bugs import active, on

HERE = Path(__file__).parent
SEED = json.loads((HERE / "seed.json").read_text())
USERS = {"alice": "secret123", "bob": "hunter22"}
DISCOUNTS = {"SAVE10": 0.10}
state = {}
app = FastAPI(title="Synthetic Shop")


class Login(BaseModel):
    username: str
    password: str


class Item(BaseModel):
    product_id: int
    quantity: int = 1


class OrderIn(BaseModel):
    discount_code: Optional[str] = None


def reset_state():
    state.update(products={p["id"]: dict(p) for p in SEED}, tokens={}, carts={}, orders={})


reset_state()


def current_user(authorization):
    token = (authorization or "").removeprefix("Bearer ")
    if token not in state["tokens"]:
        raise HTTPException(401, "login required")
    return state["tokens"][token]


def cart_view(user):
    lines, total = [], 0.0
    for pid, qty in state["carts"].get(user, {}).items():
        p = state["products"][pid]
        line_total = p["price"] if on(2) else p["price"] * qty
        total += line_total
        lines.append({"product_id": pid, "name": p["name"], "quantity": qty,
                      "price": p["price"], "line_total": round(line_total, 2)})
    return {"items": lines, "total": round(total, 2)}


@app.get("/", response_class=HTMLResponse)
def index():
    return (HERE / "static" / "index.html").read_text()


@app.get("/api/health")
def health():
    return {"status": "ok", "bugs": sorted(active())}


@app.post("/api/reset")
def reset():
    reset_state()
    return {"status": "reset"}


@app.get("/api/products")
def products():
    items = list(state["products"].values())
    return items[:-1] if on(6) else items


@app.get("/api/products/{pid}")
def product(pid: int):
    if pid not in state["products"]:
        raise HTTPException(404, "product not found")
    return state["products"][pid]


@app.post("/api/login")
def login(body: Login):
    known = body.username in USERS
    if not known or not (on(1) or USERS[body.username] == body.password):
        raise HTTPException(401, "invalid credentials")
    token = secrets.token_hex(16)
    state["tokens"][token] = body.username
    return {"token": token}


@app.get("/api/cart")
def get_cart(authorization: Optional[str] = Header(None)):
    return cart_view(current_user(authorization))


@app.post("/api/cart/items", status_code=201)
def add_item(item: Item, authorization: Optional[str] = Header(None)):
    user = current_user(authorization)
    p = state["products"].get(item.product_id)
    if p is None:
        raise HTTPException(404, "product not found")
    invalid = item.quantity == 0 if on(3) else item.quantity < 1
    if invalid:
        raise HTTPException(422, "quantity must be at least 1")
    cart = state["carts"].setdefault(user, {})
    new_qty = cart.get(p["id"], 0) + item.quantity
    if not on(4) and new_qty > p["stock"]:
        raise HTTPException(409, "insufficient stock")
    cart[p["id"]] = new_qty
    return cart_view(user)


@app.delete("/api/cart")
def clear_cart(authorization: Optional[str] = Header(None)):
    user = current_user(authorization)
    state["carts"][user] = {}
    return cart_view(user)


@app.post("/api/orders", status_code=201)
def create_order(body: OrderIn, authorization: Optional[str] = Header(None)):
    user = current_user(authorization)
    view = cart_view(user)
    if not view["items"]:
        raise HTTPException(400, "cart is empty")
    code = body.discount_code
    if code and code not in DISCOUNTS:
        raise HTTPException(400, "invalid discount code")
    rate = 0.0 if on(5) else DISCOUNTS.get(code or "", 0.0)
    for line in view["items"]:
        state["products"][line["product_id"]]["stock"] -= line["quantity"]
    oid = len(state["orders"]) + 1
    order = {"id": oid, "user": user, "items": view["items"], "discount_code": code,
             "total": round(view["total"] * (1 - rate), 2)}
    state["orders"][oid] = order
    state["carts"][user] = {}
    return order


@app.get("/api/orders/{oid}")
def get_order(oid: int, authorization: Optional[str] = Header(None)):
    user = current_user(authorization)
    order = state["orders"].get(oid)
    if order is None or order["user"] != user:
        raise HTTPException(404, "order not found")
    return order
