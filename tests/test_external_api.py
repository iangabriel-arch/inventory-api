"""
tests/test_external_api.py

Unit tests for external_api.py, using unittest.mock to simulate
OpenFoodFacts API responses so tests don't depend on the real
network or the API being available.
"""

import sys
import os
from unittest.mock import patch, Mock
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import external_api


@patch("external_api.requests.get")
def test_fetch_product_by_barcode_found(mock_get):
    """Simulates a successful OpenFoodFacts lookup."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar"
        }
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = external_api.fetch_product_by_barcode("0025293001165")

    assert result is not None
    assert result["name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    assert result["barcode"] == "0025293001165"
    mock_get.assert_called_once()


@patch("external_api.requests.get")
def test_fetch_product_by_barcode_not_found(mock_get):
    """Simulates OpenFoodFacts returning status 0 (product doesn't exist)."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": 0}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = external_api.fetch_product_by_barcode("0000000000000")

    assert result is None


@patch("external_api.requests.get")
def test_fetch_product_by_barcode_network_error(mock_get):
    """Simulates a network failure (timeout, connection error, etc.)."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Network down")

    result = external_api.fetch_product_by_barcode("0025293001165")

    assert result is None


@patch("external_api.requests.get")
def test_fetch_products_by_name_found(mock_get):
    """Simulates a successful search returning multiple products."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "products": [
            {"product_name": "Almond Milk", "brands": "Silk", "code": "111"},
            {"product_name": "Almond Milk Unsweetened", "brands": "Califia", "code": "222"},
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    results = external_api.fetch_products_by_name("almond milk")

    assert len(results) == 2
    assert results[0]["name"] == "Almond Milk"
    assert results[1]["brand"] == "Califia"


@patch("external_api.requests.get")
def test_fetch_products_by_name_no_results(mock_get):
    """Simulates a search with zero matches."""
    mock_response = Mock()
    mock_response.json.return_value = {"products": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    results = external_api.fetch_products_by_name("nonexistentproductxyz")

    assert results == []


@patch("external_api.requests.get")
def test_fetch_products_by_name_network_error(mock_get):
    """Simulates a network failure during search."""
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    results = external_api.fetch_products_by_name("almond milk")

    assert results == []
