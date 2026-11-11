"""S01: list/search products, BCC (5 cases) plus two valid boundary probes."""

from uuid import uuid4

import pytest

from shop_support import assert_error, assert_store_product


# Goal: verify the selected per_page/search block, its exact status and response content.
@pytest.mark.parametrize(
    "per_page,search_kind,expected_status",
    [
        # Goal: base — a normal page size and our product's unique name returns exactly that product.
        pytest.param(10, "match", 200, id="S01-01-base-valid-and-match"),
        # Goal: per_page=0 is below the documented minimum 1 and is rejected with 400.
        pytest.param(0, "match", 400, id="S01-02-below-minimum"),
        # Goal: per_page=101 is above the documented maximum 100 and is rejected with 400.
        pytest.param(101, "match", 400, id="S01-03-above-maximum"),
        # Goal: without a search term the list still returns valid products, at most per_page.
        pytest.param(10, "omitted", 200, id="S01-04-search-omitted"),
        # Goal: a search term that matches no product returns an empty list, not an error.
        pytest.param(10, "no-match", 200, id="S01-05-search-no-match"),
        # Goal: the lowest valid page size (1) is accepted and still finds our product.
        pytest.param(1, "match", 200, id="S01-06-lower-valid-boundary"),
        # Goal: the highest valid page size (100) is accepted and still finds our product.
        pytest.param(100, "match", 200, id="S01-07-upper-valid-boundary"),
    ],
)
def test_list_products(api, products, per_page, search_kind, expected_status):
    product = products.create("publish")
    query = {"per_page": per_page}
    if search_kind == "match":
        query["search"] = product["name"]
    elif search_kind == "no-match":
        query["search"] = "nomatch" + uuid4().hex
    response = api.store("GET", "/products", params=query)
    if expected_status == 400:
        error = assert_error(response, 400, "rest_invalid_param")
        assert "per_page" in error["data"]["params"]
        return
    assert response.status_code == 200, response.text[:500]
    body = response.json()
    assert isinstance(body, list)
    assert len(body) <= per_page
    assert all(type(item.get("id")) is int and isinstance(item.get("name"), str) for item in body)
    if search_kind == "match":
        assert len(body) == 1, "A run-unique product name should match exactly our fixture"
        assert_store_product(body[0], product)
    elif search_kind == "no-match":
        assert body == []
    else:
        assert body, "At least the published fixture exists, but no fixed catalog total is assumed"
