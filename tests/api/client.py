import requests


class Api:
    def __init__(self, base):
        self.base = base
        self.s = requests.Session()

    def login(self, username, password):
        r = self.post("/api/login", json={"username": username, "password": password})
        if r.ok:
            self.s.headers["Authorization"] = "Bearer " + r.json()["token"]
        return r

    def get(self, path, **kw):
        return self.s.get(self.base + path, timeout=10, **kw)

    def post(self, path, **kw):
        return self.s.post(self.base + path, timeout=10, **kw)

    def delete(self, path, **kw):
        return self.s.delete(self.base + path, timeout=10, **kw)
