
# py-homebox

A Python client library for the [Homebox](https://github.com/sysadminsmedia/homebox) REST API.
Homebox is a self-hosted home inventory management system that lets you track, manage, and organise your belongings.

**py-homebox** wraps every Homebox v1 endpoint in a clean, typed Python interface backed by [Pydantic](https://docs.pydantic.dev/) models, so you get auto-completion, validation, and inline documentation out of the box.

---

## Features

- Full coverage of the Homebox v1 API (items, labels, locations, maintenance, notifiers, groups, users, reporting, label-maker, products/barcodes)
- Pydantic v2 models for all request and response payloads
- Automatic Bearer-token injection after `login()`
- Environment-variable based configuration (no hard-coded credentials)

---

## Installation

Install from PyPI:

```bash
pip install homebox
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add homebox
```
---

## Compatibility
version 0.4.0 is compatible with Homebox v0.24.0 API.

version 0.3.0 is compatible with Homebox v0.23.0 API.

version 0.2.0 is compatible with Homebox v0.22.0 API.

version 0.1.0 is compatible with Homebox v0.21.0 API.

For newer additions to the Homebox API, we will release updates to this client library.

---

## Environment variables

The client reads two optional environment variables so that credentials are never hard-coded in your scripts:

| Variable        | Required | Description                                                          |
|-----------------|----------|----------------------------------------------------------------------|
| `HOMEBOX_URL`   | **Yes**  | Base URL of the Homebox API (e.g. `https://demo.homebox.software/api`) |
| `HOMEBOX_TOKEN` | No       | Pre-obtained Bearer token. Omit this and call `client.login()` instead. |

Set them in your shell before running your script:

```bash
export HOMEBOX_URL="https://demo.homebox.software/api"
export HOMEBOX_TOKEN="your-bearer-token"   # optional
```

Or store them in a `.env` file and load it with a tool such as [python-dotenv](https://pypi.org/project/python-dotenv/):

```python
from dotenv import load_dotenv
load_dotenv()   # reads .env into os.environ

from homebox import HomeboxClient
client = HomeboxClient()   # picks up HOMEBOX_URL and HOMEBOX_TOKEN automatically
```

---

## Quick start

### Authenticate with environment variables

```python
import os
from homebox import HomeboxClient

os.environ["HOMEBOX_URL"] = "https://demo.homebox.software/api"
os.environ["HOMEBOX_TOKEN"] = "your-bearer-token"

client = HomeboxClient()
```

### Authenticate by passing arguments directly

```python
from homebox import HomeboxClient

client = HomeboxClient(
    base_url="https://demo.homebox.software/api",
    token="your-bearer-token",
)
```

Explicit arguments always take precedence over environment variables.

### Authenticate with username and password

If you do not have a token yet, log in with your credentials:

```python
from homebox import HomeboxClient

client = HomeboxClient(base_url="https://demo.homebox.software/api")
client.login("admin@admin.com", "admin")

# subsequent calls now carry the Bearer token automatically
```

---

## Usage examples

### Items

```python
# List all items (paginated)
result = client.items.query_all_items()
for item in result.items or []:
    print(item.name, item.location)

# Search for items by name
result = client.items.query_all_items(q="laptop")

# Filter by label and location
result = client.items.query_all_items(
    labels=["label-uuid-1", "label-uuid-2"],
    locations=["location-uuid-1"],
    page=1,
    pageSize=50,
)

# Create an item
from homebox.models import ItemCreate
new_item = client.items.create_item(ItemCreate(
    name="MacBook Pro",
    description="Work laptop",
    quantity=1,
    locationId="location-uuid",
))
print(new_item.id)

# Get full item details
item = client.items.get_item("item-uuid")

# Update an item
from homebox.models import ItemUpdate
client.items.update_item("item-uuid", ItemUpdate(name="MacBook Pro M3"))

# Delete an item
client.items.delete_item("item-uuid")

# Export all items as CSV
csv_data = client.items.export_items()
with open("items.csv", "w") as f:
    f.write(csv_data)

# Import items from CSV
with open("items.csv", "rb") as f:
    client.items.import_items(f.read())
```

### Labels

```python
from homebox.models import LabelCreate

# List all labels
labels = client.labels.get_all_labels()

# Create a label
label = client.labels.create_label(LabelCreate(name="Electronics", color="#0ea5e9"))

# Delete a label
client.labels.delete_label(label.id)
```

### Locations

```python
from homebox.models import LocationCreate

# List all locations
locations = client.locations.get_all_locations()

# List only root (top-level) locations
roots = client.locations.get_all_locations(filterChildren=True)

# Get the full location tree (with nested children)
tree = client.locations.get_locations_tree()

# Create a location
office = client.locations.create_location(LocationCreate(name="Office"))

# Create a nested location
desk = client.locations.create_location(
    LocationCreate(name="Desk", parentId=office.id)
)
```

### Maintenance log

```python
from homebox.models import MaintenanceEntryCreate, MaintenanceFilterStatus

# Add a maintenance entry to an item
entry = client.items.create_maintenance_entry(
    "item-uuid",
    MaintenanceEntryCreate(
        name="Annual service",
        scheduledDate="2025-06-01",
        cost="150.00",
    ),
)

# List only scheduled maintenance entries across all items
scheduled = client.maintenance.query_all_maintenance(
    status=MaintenanceFilterStatus.MaintenanceFilterStatusScheduled
)
```

### Group statistics

```python
stats = client.groups.get_group_statistics()
print(f"Total items: {stats.totalItems}")
print(f"Total value: {stats.totalItemPrice}")

# Purchase price over time
from_stats = client.groups.get_purchase_price_statistics(start="2024-01-01", end="2024-12-31")
for entry in from_stats.entries or []:
    print(entry.date, entry.value)
```

### Notifiers (webhooks)

```python
from homebox.models import NotifierCreate

# Create a new webhook notifier
notifier = client.notifiers.create_notifier(NotifierCreate(
    name="My Discord Webhook",
    url="https://discord.com/api/webhooks/...",
    isActive=True,
))

# Send a test notification
client.notifiers.test_notifier(notifier.url)
```

### Attachments

```python
# Upload a photo attachment
with open("photo.jpg", "rb") as f:
    client.items.create_item_attachment(
        "item-uuid",
        file=f.read(),
        type="photo",
        primary=True,
        name="Front view",
    )
```

### Barcode / QR code

```python
# Look up a product by EAN barcode
products = client.products.search_ean_from_barcode("0012345678905")
for product in products:
    print(product.manufacturer, product.modelNumber)

# Generate a QR code
qr_svg = client.products.create_qr_code("https://example.com")
```

### Reporting

```python
# Export a Bill of Materials CSV
bom = client.reporting.export_bill_of_materials()
with open("bom.csv", "w") as f:
    f.write(bom)
```

### Label maker

```python
# Get a printable label for an item
label_svg = client.labelmaker.get_item_label("item-uuid", print=True)
```

### User management

```python
from homebox.models import UserUpdate, ChangePassword

# Get the current user
me = client.users.get_user_self()
print(me.name, me.email)

# Update profile
client.users.update_account(UserUpdate(name="Alice Smith"))

# Change password
client.users.change_password(ChangePassword(current="old", new="new-secret"))

# Log out
client.users.user_logout()
```

## Contributing

Pull requests are welcome.
Make sure you install the pre-commit hooks and linters to maintain code quality and consistency:

```bash
uv sync --group dev
pre-commit install
```
And make sure all tests pass before submitting a PR:
