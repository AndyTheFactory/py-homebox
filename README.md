
# py-homebox

A Python client library for the [Homebox](https://github.com/sysadminsmedia/homebox) REST API.
Homebox is a self-hosted home inventory management system that lets you track, manage, and organise your belongings.

**py-homebox** wraps every Homebox v1 endpoint in a clean, typed Python interface backed by [Pydantic](https://docs.pydantic.dev/) models, so you get auto-completion, validation, and inline documentation out of the box.

---

## Features

- Full coverage of the Homebox v1 API (entities, entity types, tags, maintenance, imports/exports, notifiers, groups, users, reporting, label-maker, products/barcodes)
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
version 0.6.0 is compatible with Homebox v0.26.0 API.

version 0.5.0 is compatible with Homebox v0.25.0 API.

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

### Entities

```python
# List all entities (items and locations, paginated)
result = client.entities.query_all_entities()
for entity in result.items or []:
    print(entity.name, entity.entityType)

# Search and filter entities
result = client.entities.query_all_entities(
    q="laptop",
    tags=["tag-uuid-1"],
    parentIds=["location-uuid-1"],
)

# Create a location-like entity type
from homebox.models import EntityTypeCreate
location_type = client.entity_types.create_entity_type(
    EntityTypeCreate(name="Location", icon="warehouse", isLocation=True)
)

# Create an entity
from homebox.models import EntityCreate
new_item = client.entities.create_entity(EntityCreate(
    name="MacBook Pro",
    description="Work laptop",
    quantity=1,
    entityTypeId="device-type-uuid",
    parentId="location-uuid",
))
print(new_item.id)

# Get and update full entity details
entity = client.entities.get_entity("entity-uuid")

from homebox.models import EntityUpdate
client.entities.update_entity("entity-uuid", EntityUpdate(name="MacBook Pro M3"))

# Delete an entity
client.entities.delete_entity("entity-uuid")

# Export all entities as CSV
csv_data = client.entities.export_entities()
with open("entities.csv", "w") as f:
    f.write(csv_data)

# Import entities from CSV
with open("entities.csv", "rb") as f:
    client.entities.import_entities(f.read())
```

The legacy `client.items` and `client.locations` namespaces remain available as
compatibility adapters and send requests to the v0.26 entity endpoints.

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

### Location-like entities

```python
from homebox.models import EntityCreate

# Find a configured location entity type
location_type = next(t for t in client.entity_types.get_all_entity_types() if t.isLocation)

# Get the full entity tree
tree = client.entities.get_entities_tree(withItems=True)

# Create a location-like entity
office = client.entities.create_entity(
    EntityCreate(name="Office", entityTypeId=location_type.id)
)

# Create a nested location-like entity
desk = client.entities.create_entity(
    EntityCreate(name="Desk", entityTypeId=location_type.id, parentId=office.id)
)
```

### Maintenance log

```python
from homebox.models import MaintenanceEntryCreate, MaintenanceFilterStatus

# Add a maintenance entry to an entity
entry = client.entities.create_maintenance_entry(
    "entity-uuid",
    MaintenanceEntryCreate(
        name="Annual service",
        scheduledDate="2025-06-01",
        cost="150.00",
    ),
)

# List scheduled maintenance entries across all entities
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
    client.entities.create_attachment(
        "entity-uuid",
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

# Get a printable label by asset ID (v0.5.0+ endpoint)
asset_label_svg = client.labelmaker.get_asset_label("000001", print=True)
```

### User management

```python
from homebox.models import UserUpdate, ChangePassword

# Get the current user
me = client.users.get_user_self()
print(me.name, me.email)

# Update profile
client.users.update_account(UserUpdate(name="Alice Smith", email=me.email))

# Change password
client.users.change_password(ChangePassword(current="old", new="new-secret"))

# Read and update arbitrary per-user settings
settings = client.users.get_user_settings()
settings_payload = settings.model_dump(exclude_none=True)
settings_payload["ui.table.pageSize"] = 50
client.users.update_user_settings(settings_payload)

# Create and later revoke a personal API key (v0.26.0)
from homebox.models import APIKeyCreate
api_key = client.users.create_api_key(APIKeyCreate(name="Automation"))
client.users.delete_api_key(api_key.id)

# Log out
client.users.user_logout()
```

### Collection exports

```python
# Start an asynchronous collection export and poll its status
export = client.group_exports.start_export()
export = client.group_exports.get_export(export.id)

if export.status == "completed":
    archive = client.group_exports.download_export(export.id)
```

## Contributing

Pull requests are welcome.
Make sure you install the pre-commit hooks and linters to maintain code quality and consistency:

```bash
uv sync --group dev
pre-commit install
```
And make sure all tests pass before submitting a PR:
