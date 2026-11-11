"""HTTP and disposable-product fixtures; never modify the WooCommerce application."""

from datetime import datetime, timezone
import json
from urllib.parse import urlsplit
from uuid import uuid4

import requests


def is_owned_product(product, expected_name, run_id):
    """Allow cleanup only for an exact G05 name, numeric ID and matching run marker."""
    return (
        isinstance(product, dict)
        and type(product.get("id")) is int
        and product["id"] > 0
        and expected_name.startswith(f"G05-{run_id}-")
        and product.get("name") == expected_name
        and any(
            isinstance(entry, dict)
            and entry.get("key") == "itcs386_test_run"
            and entry.get("value") == run_id
            for entry in product.get("meta_data", [])
        )
    )


def assert_error(response, expected_status, expected_code=None):
    """Assert an exact HTTP status and meaningful JSON error fields."""
    assert response.status_code == expected_status, response.text[:500]
    body = response.json()
    assert isinstance(body, dict)
    assert isinstance(body.get("code"), str) and body["code"]
    assert isinstance(body.get("message"), str) and body["message"]
    if expected_code is not None:
        assert body["code"] == expected_code
    assert body.get("data", {}).get("status") == expected_status
    return body


def assert_store_product(body, expected):
    """Compare shopper-visible identity and price against known fixture inputs."""
    assert body["id"] == expected["id"]
    assert body["name"] == expected["name"]
    assert body["prices"]["currency_code"] == "THB"
    assert body["prices"]["currency_minor_unit"] == 2
    assert body["prices"]["regular_price"] == "10000"  # 100.00 THB in minor units.


class ShopAPI:
    """Separate public/admin sessions; no auth on Store calls, redirects or retries."""

    def __init__(self, base_url, username, password):
        parsed = urlsplit(base_url)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("SHOP_BASE_URL must be a shop URL without credentials/query/fragment")
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.sessions = {"store": requests.Session(), "admin": requests.Session()}
        for session in self.sessions.values():
            session.trust_env = False  # No implicit netrc credentials or proxy configuration.

    def close(self):
        for session in self.sessions.values():
            session.close()

    def _request(self, kind, method, path, auth_mode="valid", **kwargs):
        namespace = "wc/store/v1" if kind == "store" else "wc/v3"
        auth = None
        if kind == "admin" and auth_mode == "valid":
            auth = (self.username, self.password)
        elif kind == "admin" and auth_mode == "wrong":
            auth = (self.username, "deliberately-invalid-" + uuid4().hex)
        elif auth_mode not in {"valid", "missing"}:
            raise ValueError("Unknown authentication mode")
        response = self.sessions[kind].request(
            method,
            f"{self.base_url}/wp-json/{namespace}{path}",
            auth=auth,
            allow_redirects=False,
            timeout=(5, 20),
            **kwargs,
        )
        try:
            body = response.json()
        except ValueError:
            summary = {"format": "non-JSON"}
        else:
            if isinstance(body, list):
                summary = {"count": len(body), "ids": [p.get("id") for p in body if isinstance(p, dict)]}
            elif isinstance(body, dict):
                summary = {k: body[k] for k in ("id", "name", "sku", "status", "regular_price", "prices", "code", "message") if k in body}
            else:
                summary = {"format": type(body).__name__}
        print(json.dumps({
            "time_utc": datetime.now(timezone.utc).isoformat(),
            "method": method, "path": f"/{namespace}{path}",
            "query": kwargs.get("params"), "input": kwargs.get("json"),
            "auth_mode": auth_mode if kind == "admin" else "public/no-auth",
            "status": response.status_code, "response": summary,
        }, ensure_ascii=False), flush=True)
        return response

    def store(self, method, path, **kwargs):
        return self._request("store", method, path, **kwargs)

    def admin(self, method, path, **kwargs):
        return self._request("admin", method, path, **kwargs)


class ProductFactory:
    """Track exact created IDs/SKUs, and verify ownership again before deletion."""

    def __init__(self, api, run_id):
        self.api = api
        self.run_id = run_id
        self.pending = {}
        self.created = {}
        self.uncertain = set()

    def payload(self, status="publish"):
        marker = uuid4().hex
        return {
            "name": f"G05-{self.run_id}-{marker}",
            "sku": "g05" + marker,
            "type": "simple", "status": status, "regular_price": "100.00",
            "catalog_visibility": "visible",
            "meta_data": [{"key": "itcs386_test_run", "value": self.run_id}],
        }

    def submit(self, payload, auth_mode="valid"):
        # Register before POST: an interrupted response must NOT cause a blind POST retry.
        self.pending[payload["sku"]] = payload["name"]
        self.uncertain.add(payload["sku"])
        print(f"PREPARE own product: sku={payload['sku']} name={payload['name']}", flush=True)
        response = self.api.admin("POST", "/products", json=payload, auth_mode=auth_mode)
        try:
            body = response.json()
        except ValueError:
            return response
        if isinstance(body, dict) and type(body.get("id")) is int and body["id"] > 0:
            self.created[body["id"]] = payload["name"]
            self.pending.pop(payload["sku"], None)
            self.uncertain.discard(payload["sku"])
        elif response.status_code in {400, 401, 403}:
            self.uncertain.discard(payload["sku"])
        return response

    def create(self, status="publish"):
        payload = self.payload(status)
        response = self.submit(payload)
        assert response.status_code == 201, response.text[:500]
        body = response.json()
        assert is_owned_product(body, payload["name"], self.run_id), "Created product ownership was not verified"
        assert body["status"] == status
        return body

    def lookup(self, sku):
        response = self.api.admin("GET", "/products", params={"sku": sku, "per_page": 2, "status": "any"})
        assert response.status_code == 200, response.text[:500]
        body = response.json()
        assert isinstance(body, list)
        expected_name = self.pending.get(sku)
        for product in body:
            if expected_name and is_owned_product(product, expected_name, self.run_id):
                self.created[product["id"]] = expected_name
        if not body and sku not in self.uncertain:
            self.pending.pop(sku, None)
        return body

    def delete_owned(self, product_id):
        expected_name = self.created[product_id]  # Never accept an arbitrary product ID.
        response = self.api.admin("GET", f"/products/{product_id}")
        if response.status_code == 404:
            del self.created[product_id]
            return
        assert response.status_code == 200, response.text[:500]
        assert is_owned_product(response.json(), expected_name, self.run_id), (
            f"Refusing to delete product {product_id}: exact ownership check failed"
        )
        response = self.api.admin("DELETE", f"/products/{product_id}", params={"force": "true"})
        assert response.status_code == 200, response.text[:500]
        assert response.json()["id"] == product_id
        absent = self.api.admin("GET", f"/products/{product_id}")
        assert_error(absent, 404)
        del self.created[product_id]

    def cleanup(self):
        errors = []
        # Reconcile an ambiguous POST by its exact unique SKU; never search-and-delete by G05 alone.
        for sku in list(self.pending):
            try:
                found = self.lookup(sku)
                if any(p.get("id") not in self.created for p in found):
                    raise AssertionError(f"Unresolved ownership for exact SKU {sku}")
                if not found and sku in self.uncertain:
                    raise AssertionError("POST outcome unknown; an empty lookup is not proof of absence")
                self.pending.pop(sku, None)
                self.uncertain.discard(sku)
            except Exception as exc:
                errors.append(f"SKU {sku}: {type(exc).__name__}: {exc}")
        for product_id in list(self.created):
            try:
                self.delete_owned(product_id)
            except Exception as exc:
                errors.append(f"ID {product_id}: {type(exc).__name__}: {exc}")
        assert not errors, "Cleanup needs attention (no unsafe deletion attempted): " + "; ".join(errors)
        print("CLEANUP verified: no products from this test remain", flush=True)
