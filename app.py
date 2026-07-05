"""
app.py

Flask REST API for the Inventory Management System.
"""
from flask import Flask, jsonify, request
import data_store
import external_api

from flask import Flask, jsonify, request
import data_store

app = Flask(__name__)


@app.route("/inventory", methods=["GET"])
def get_inventory():
    """Fetch all inventory items."""
    return jsonify(data_store.get_all_items()), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Fetch a single inventory item by ID."""
    item = data_store.get_item_by_id(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def create_item():
    """Add a new inventory item."""
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "Request body must include at least 'name'"}), 400

    new_item = data_store.add_item(data)
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    """Update one or more fields of an existing item."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Request body must contain JSON"}), 400

    updated_item = data_store.update_item(item_id, data)

    if updated_item is None:
        return jsonify({"error": "Item not found"}), 404

    return jsonify(updated_item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Remove an item from inventory."""
    deleted = data_store.delete_item(item_id)

    if not deleted:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({"message": f"Item {item_id} deleted"}), 200

@app.route("/inventory/lookup/barcode/<barcode>", methods=["GET"])
def lookup_by_barcode(barcode):
    """Look up a product on OpenFoodFacts by barcode (does NOT save it)."""
    product = external_api.fetch_product_by_barcode(barcode)

    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    return jsonify(product), 200


@app.route("/inventory/lookup/name/<name>", methods=["GET"])
def lookup_by_name(name):
    """Search OpenFoodFacts by product name (does NOT save it)."""
    products = external_api.fetch_products_by_name(name)

    if not products:
        return jsonify({"error": "No products found"}), 404

    return jsonify(products), 200


@app.route("/inventory/import/barcode/<barcode>", methods=["POST"])
def import_by_barcode(barcode):
    """
    Fetch a product from OpenFoodFacts by barcode and add it
    directly to the inventory array.
    """
    product = external_api.fetch_product_by_barcode(barcode)

    if product is None:
        return jsonify({"error": "Product not found on OpenFoodFacts"}), 404

    # Allow overriding price/stock at import time, since OpenFoodFacts
    # doesn't provide retail price or stock levels.
    body = request.get_json(silent=True) or {}
    product["price"] = body.get("price", 0)
    product["stock"] = body.get("stock", 0)

    new_item = data_store.add_item(product)
    return jsonify(new_item), 201


if __name__ == "__main__":
    app.run(debug=True)