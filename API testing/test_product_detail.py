"""S02: read one product by positive-integer ID, BCC over resource state (C1) and `context` (C2)."""

import pytest

from shop_support import assert_error, assert_store_product


# Goal: expose the known published product, but not a draft or a verified absent resource,
# and validate the documented `context` query parameter of this route.
@pytest.mark.parametrize(
    "resource_state,context_kind,expected_status",
    [
        # Goal: base — a published product read without `context` returns its exact ID, name and price.
        pytest.param("publish", "omitted", 200, id="S02-01-existing-published"),
        # Goal: an existing draft must stay hidden from the public Store API (404).
        pytest.param("draft", "omitted", 404, id="S02-02-existing-draft"),
        # Goal: an ID whose product was deleted and verified absent returns a JSON 404 error.
        pytest.param("absent", "omitted", 404, id="S02-03-verified-absent"),
        # Goal: an explicitly supplied valid `context=view` is accepted and returns the same product.
        pytest.param("publish", "valid", 200, id="S02-04-context-explicit-valid"),
        # Goal: a `context` value outside the documented enum is rejected with 400 rest_invalid_param.
        pytest.param("publish", "invalid", 400, id="S02-05-context-invalid-value"),
    ],
)
def test_product_detail(api, products, resource_state, context_kind, expected_status):
    product = products.create("publish" if resource_state == "publish" else "draft")
    if resource_state == "absent":
        # Delete this exact owned record and verify Admin 404 before testing Store 404.
        products.delete_owned(product["id"])
    else:
        precondition = api.admin("GET", f"/products/{product['id']}")
        assert precondition.status_code == 200
        assert precondition.json()["status"] == resource_state
    params = None
    if context_kind == "valid":
        params = {"context": "view"}
    elif context_kind == "invalid":
        params = {"context": "not-a-context"}
    response = api.store("GET", f"/products/{product['id']}", params=params)
    if expected_status == 200:
        assert response.status_code == 200, response.text[:500]
        assert_store_product(response.json(), product)
    elif expected_status == 400:
        error = assert_error(response, 400, "rest_invalid_param")
        assert "context" in error["data"]["params"]
    else:
        assert_error(response, 404)
