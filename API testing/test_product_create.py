"""S03: create a simple product, varying authentication/publication with BCC."""

from decimal import Decimal

import pytest

from shop_support import assert_error, assert_store_product, is_owned_product


# Goal: save correct product data for valid input; reject invalid input/auth without creating data.
@pytest.mark.parametrize(
    "auth_mode,status,expected_status",
    [
        # Goal: base — correct credentials create a published product with the exact saved data.
        pytest.param("valid", "publish", 201, id="S03-01-base-valid-published"),
        # Goal: a create request without credentials is rejected (401) and creates nothing.
        pytest.param("missing", "publish", 401, id="S03-02-credentials-absent"),
        # Goal: a create request with a wrong password is rejected (401) and creates nothing.
        pytest.param("wrong", "publish", 401, id="S03-03-credentials-wrong"),
        # Goal: a valid draft is created but stays hidden from the public Store API.
        pytest.param("valid", "draft", 201, id="S03-04-valid-unpublished"),
        # Goal: an unknown status value is rejected with 400 and creates nothing.
        pytest.param("valid", "not-a-status", 400, id="S03-05-invalid-publication-status"),
    ],
)
def test_create_product(api, products, auth_mode, status, expected_status):
    payload = products.payload(status)
    response = products.submit(payload, auth_mode)
    if expected_status != 201:
        error = assert_error(response, expected_status, "rest_invalid_param" if expected_status == 400 else None)
        if expected_status == 400:
            assert "status" in error["data"]["params"]
        assert products.lookup(payload["sku"]) == [], "A rejected create must not leave a product"
        return
    assert response.status_code == 201, response.text[:500]
    body = response.json()
    assert is_owned_product(body, payload["name"], products.run_id)
    assert body["type"] == "simple"
    assert body["status"] == status
    assert body["sku"] == payload["sku"]
    assert Decimal(body["regular_price"]) == Decimal("100.00")
    saved = api.admin("GET", f"/products/{body['id']}")
    assert saved.status_code == 200
    assert saved.json()["name"] == payload["name"]
    assert saved.json()["status"] == status
    assert Decimal(saved.json()["regular_price"]) == Decimal("100.00")
    shopper_view = api.store("GET", f"/products/{body['id']}")
    if status == "publish":
        assert shopper_view.status_code == 200
        assert_store_product(shopper_view.json(), body)
    else:
        assert_error(shopper_view, 404)
