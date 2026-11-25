"""Seeded bugs. Enable with BUGS=1,3 (comma separated). Default: none."""
import os

BUGS = {
    "1": ("Login accepts any password for a known user", "REQ-02"),
    "2": ("Cart line total ignores quantity", "REQ-03"),
    "3": ("Negative quantity accepted in cart", "REQ-03"),
    "4": ("Out-of-stock products can be added to cart", "REQ-03"),
    "5": ("Discount code SAVE10 is not applied to the order total", "REQ-04"),
    "6": ("Product list omits the last product", "REQ-01"),
}


def active():
    return {b.strip() for b in os.getenv("BUGS", "").split(",") if b.strip()}


def on(n):
    return str(n) in active()
