"""
external_api.py

Handles communication with the OpenFoodFacts API to fetch real
product details by barcode or by name/search term.
"""
import requests

BASE_URL = "https://world.openfoodfacts.org"
HEADERS = {
    "User-Agent": "InventoryManagementLab/1.0 (student project; contact: example@example.com)"
}


def fetch_product_by_barcode(barcode):
    """
    Look up a single product by its barcode.
    Returns a dict of product info, or None if not found / request failed.
    """
    url = f"{BASE_URL}/api/v2/product/{barcode}.json"

    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error contacting OpenFoodFacts: {e}")
        return None

    data = response.json()

    if data.get("status") != 1:
        # status 0 means product not found
        return None

    product = data.get("product", {})
    return {
        "name": product.get("product_name"),
        "brand": product.get("brands"),
        "ingredients": product.get("ingredients_text"),
        "barcode": barcode,
    }


def fetch_products_by_name(name, limit=5):
    """
    Search for products by name. Returns a list of matching product dicts
    (may be empty if nothing found or request failed).
    """
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error contacting OpenFoodFacts: {e}")
        return []

    data = response.json()
    products = data.get("products", [])

    results = []
    for product in products[:limit]:
        results.append({
            "name": product.get("product_name"),
            "brand": product.get("brands"),
            "ingredients": product.get("ingredients_text"),
            "barcode": product.get("code"),
        })

    return results
