"""Test data factory for the synthetic shop."""
import json
import random
from pathlib import Path

SEED = Path(__file__).resolve().parent.parent / "app" / "seed.json"


class DataFactory:
    def __init__(self, seed=7):
        self.rng = random.Random(seed)
        self.products = json.loads(SEED.read_text())

    def user(self, valid=True):
        pw = "secret123" if valid else f"wrong-{self.rng.randint(1000, 9999)}"
        return {"username": "alice", "password": pw}

    def product(self, in_stock=True, pid=None):
        if pid is not None:
            return next(p for p in self.products if p["id"] == pid)
        return next(p for p in self.products if (p["stock"] > 0) == in_stock)

    def item(self, product=None, quantity=1):
        p = product or self.product()
        return {"product_id": p["id"], "quantity": quantity}
