"""Every case receives an independent HTTP client and disposable product factory."""

import os
import re
from uuid import uuid4

import pytest

from shop_support import ProductFactory, ShopAPI


@pytest.fixture(scope="session")
def shop_config():
    user = os.environ.get("SHOP_USER")
    password = os.environ.get("SHOP_API_PASSWORD")
    if not user or not password:
        pytest.fail("Set SHOP_USER and SHOP_API_PASSWORD before running; use the Shop API password, not the browser password.", pytrace=False)
    if user != "itcs386-g05":
        pytest.fail("These G05 fixtures require the assigned itcs386-g05 account.", pytrace=False)
    run_id = os.environ.get("SHOP_TEST_RUN_ID", uuid4().hex[:16])
    if not re.fullmatch(r"[a-f0-9]{16,32}", run_id):
        pytest.fail("SHOP_TEST_RUN_ID must be 16-32 lowercase hexadecimal characters.", pytrace=False)
    config = (os.environ.get("SHOP_BASE_URL", "http://157.85.102.236/shop"), user, password, run_id)
    preflight = ShopAPI(*config[:3])
    try:
        response = preflight.admin("GET", "/products", params={"per_page": 1})
        assert response.status_code == 200, "Admin read preflight failed; no test products have been created"
        assert isinstance(response.json(), list)
    finally:
        preflight.close()
    return config


@pytest.fixture
def api(shop_config):
    client = ShopAPI(*shop_config[:3])
    yield client
    client.close()


@pytest.fixture
def products(api, shop_config):
    factory = ProductFactory(api, shop_config[3])
    try:
        yield factory
    finally:
        factory.cleanup()
