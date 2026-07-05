"""
cli.py

Command-line interface for the Inventory Management System.
Talks to the Flask API over HTTP using the `requests` library,
just like any other client would.

Run the Flask server first (python app.py), then run this in another terminal:
    python cli.py
"""

import requests

BASE_URL = "http://127.0.0.1:5000"


def list_items():
    response = requests.get(f"{BASE_URL}/inventory")
    items = response.json()

    if not items:
        print("\nInventory is empty.\n")
        return

    print("\n--- Inventory ---")
    for item in items:
        print(f"[{item['id']}] {item['name']} | {item.get('brand', 'N/A')} "
              f"| ${item.get('price', 0)} | stock: {item.get('stock', 0)}")
    print()


def view_item():
    item_id = input("Enter item ID: ").strip()
    response = requests.get(f"{BASE_URL}/inventory/{item_id}")

    if response.status_code == 404:
        print("\nItem not found.\n")
        return

    item = response.json()
    print("\n--- Item Details ---")
    for key, value in item.items():
        print(f"{key}: {value}")
    print()


def add_item():
    name = input("Product name: ").strip()
    if not name:
        print("\nName is required. Cancelled.\n")
        return

    brand = input("Brand (optional): ").strip()
    price = input("Price (optional, default 0): ").strip()
    stock = input("Stock quantity (optional, default 0): ").strip()

    payload = {"name": name}
    if brand:
        payload["brand"] = brand
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("Invalid price, skipping.")
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("Invalid stock, skipping.")

    response = requests.post(f"{BASE_URL}/inventory", json=payload)

    if response.status_code == 201:
        print("\nItem added successfully:")
        print(response.json())
    else:
        print("\nFailed to add item:", response.json())
    print()


def update_item():
    item_id = input("Enter item ID to update: ").strip()
    print("Leave a field blank to leave it unchanged.")

    price = input("New price: ").strip()
    stock = input("New stock: ").strip()

    payload = {}
    if price:
        try:
            payload["price"] = float(price)
        except ValueError:
            print("Invalid price, skipping.")
    if stock:
        try:
            payload["stock"] = int(stock)
        except ValueError:
            print("Invalid stock, skipping.")

    if not payload:
        print("\nNothing to update.\n")
        return

    response = requests.patch(f"{BASE_URL}/inventory/{item_id}", json=payload)

    if response.status_code == 200:
        print("\nItem updated:")
        print(response.json())
    elif response.status_code == 404:
        print("\nItem not found.")
    else:
        print("\nUpdate failed:", response.json())
    print()


def delete_item():
    item_id = input("Enter item ID to delete: ").strip()
    response = requests.delete(f"{BASE_URL}/inventory/{item_id}")

    if response.status_code == 200:
        print("\nItem deleted.\n")
    elif response.status_code == 404:
        print("\nItem not found.\n")
    else:
        print("\nDelete failed:", response.json())


def find_on_external_api():
    print("Search by (1) barcode or (2) name?")
    choice = input("> ").strip()

    if choice == "1":
        barcode = input("Enter barcode: ").strip()
        response = requests.get(f"{BASE_URL}/inventory/lookup/barcode/{barcode}")

        if response.status_code == 404:
            print("\nProduct not found on OpenFoodFacts.\n")
            return

        product = response.json()
        print("\n--- Found Product ---")
        for key, value in product.items():
            print(f"{key}: {value}")

        save = input("\nAdd this to your inventory? (y/n): ").strip().lower()
        if save == "y":
            price = input("Price: ").strip()
            stock = input("Stock: ").strip()
            payload = {}
            if price:
                payload["price"] = float(price)
            if stock:
                payload["stock"] = int(stock)

            import_response = requests.post(
                f"{BASE_URL}/inventory/import/barcode/{barcode}", json=payload
            )
            if import_response.status_code == 201:
                print("\nAdded to inventory:")
                print(import_response.json())
            else:
                print("\nFailed to import:", import_response.json())

    elif choice == "2":
        name = input("Enter product name: ").strip()
        response = requests.get(f"{BASE_URL}/inventory/lookup/name/{name}")

        if response.status_code == 404:
            print("\nNo products found.\n")
            return

        products = response.json()
        print("\n--- Search Results ---")
        for i, product in enumerate(products, start=1):
            print(f"{i}. {product.get('name')} ({product.get('brand')})")
        print("\n(Use option 1 with a barcode to actually import one of these.)")

    else:
        print("\nInvalid choice.\n")
    print()


def main_menu():
    while True:
        print("=" * 40)
        print("INVENTORY MANAGEMENT SYSTEM")
        print("=" * 40)
        print("1. View all items")
        print("2. View single item")
        print("3. Add new item")
        print("4. Update item")
        print("5. Delete item")
        print("6. Find item on external API (OpenFoodFacts)")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                list_items()
            elif choice == "2":
                view_item()
            elif choice == "3":
                add_item()
            elif choice == "4":
                update_item()
            elif choice == "5":
                delete_item()
            elif choice == "6":
                find_on_external_api()
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("\nInvalid option, try again.\n")
        except requests.exceptions.ConnectionError:
            print("\nCould not connect to the API. Is the Flask server running?\n")


if __name__ == "__main__":
    main_menu()
