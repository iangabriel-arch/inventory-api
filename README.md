# Inventory Management System

A Flask-based REST API for managing retail inventory, with real-time product
enrichment from the [OpenFoodFacts API](https://world.openfoodfacts.org/),
a CLI client, and a full pytest test suite.

Built as part of a summative lab covering Flask routing, CRUD operations,
external API integration, Git workflow, and automated testing.

## Features

- **REST API** built with Flask, supporting full CRUD on inventory items
- **OpenFoodFacts integration** — look up real product data by barcode or
  name, and import it directly into your inventory
- **CLI client** — a menu-driven terminal app that talks to the API over HTTP
- **Test suite** — pytest tests for every API endpoint and mocked tests for
  the external API integration (no live network needed to run tests)

## Project Structure

```
inventory-api/
├── app.py                    # Flask REST API and route definitions
├── data_store.py              # In-memory "database" (list of dicts)
├── external_api.py            # OpenFoodFacts integration
├── cli.py                     # CLI frontend
├── tests/
│   ├── test_api.py            # Tests for CRUD endpoints
│   └── test_external_api.py   # Tests for external API (mocked)
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/iangabriel-arch/inventory-api.git
cd inventory-api
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

## Running the API

Start the Flask server:

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5000`. Debug mode is enabled,
so the server auto-reloads on code changes.

> **Note:** Since inventory is stored in memory (a Python list, not a real
> database), restarting the server or triggering a debug reload will clear
> all stored items.

## API Endpoints

| Method | Endpoint                                  | Description                                      |
|--------|--------------------------------------------|---------------------------------------------------|
| GET    | `/inventory`                                | Fetch all inventory items                         |
| GET    | `/inventory/<id>`                           | Fetch a single item by ID                         |
| POST   | `/inventory`                                | Create a new item                                 |
| PATCH  | `/inventory/<id>`                           | Update one or more fields of an existing item     |
| DELETE | `/inventory/<id>`                           | Remove an item                                    |
| GET    | `/inventory/lookup/barcode/<barcode>`       | Look up a product on OpenFoodFacts (not saved)    |
| GET    | `/inventory/lookup/name/<name>`             | Search OpenFoodFacts by name (not saved)          |
| POST   | `/inventory/import/barcode/<barcode>`       | Fetch a product from OpenFoodFacts and add it to inventory |

### Example requests

**Create an item:**
```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Organic Almond Milk", "brand": "Silk", "price": 3.99, "stock": 25}'
```

**Update stock level:**
```bash
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 40}'
```

**Import a product from OpenFoodFacts by barcode:**
```bash
curl -X POST http://127.0.0.1:5000/inventory/import/barcode/3017620422003 \
  -H "Content-Type: application/json" \
  -d '{"price": 4.50, "stock": 15}'
```

## Using the CLI

With the Flask server running in one terminal, run the CLI in another:

```bash
python cli.py
```

You'll see a menu:

```
========================================
INVENTORY MANAGEMENT SYSTEM
========================================
1. View all items
2. View single item
3. Add new item
4. Update item
5. Delete item
6. Find item on external API (OpenFoodFacts)
7. Exit
```

- Options 1–5 map directly to the CRUD endpoints above.
- Option 6 lets you search OpenFoodFacts by barcode or name, preview the
  result, and choose whether to import it into your inventory (you'll be
  prompted for a price and stock level, since OpenFoodFacts doesn't know
  your retail pricing).

## Running Tests

The project includes a full pytest suite covering the API endpoints and
the external API integration (mocked with `unittest.mock`, so tests run
without any network access).

```bash
pytest -v
```

- `tests/test_api.py` — tests every CRUD endpoint, including error cases
  (missing fields, nonexistent IDs, empty request bodies)
- `tests/test_external_api.py` — mocks OpenFoodFacts responses to test
  found/not-found/network-failure scenarios without hitting the real API

## Design Notes

- **In-memory storage:** Inventory is stored as a Python list of dicts
  rather than a real database, per the lab requirements. Each item gets
  an auto-incrementing integer ID.
- **PATCH vs PUT:** Updates use PATCH semantics — only the fields included
  in the request body are changed; everything else on the item is left
  untouched.
- **External API error handling:** All calls to OpenFoodFacts are wrapped
  in `try/except` blocks to handle network failures or timeouts gracefully,
  returning `None`/an empty list instead of crashing the API.
- **User-Agent header:** OpenFoodFacts requires a descriptive `User-Agent`
  header on requests; omitting it results in `403 Forbidden` errors.

## Git Workflow

This project was developed using feature branches for each major piece
of functionality (CLI, tests), merged into `main` via pull requests:

- `feature/cli` — CLI frontend
- `feature/tests` — pytest test suite

## Future Improvements

- Replace in-memory storage with a persistent database (SQLite/Postgres)
- Add authentication for the admin portal
- Add pagination for large inventories
- Cache OpenFoodFacts lookups to reduce redundant external calls
