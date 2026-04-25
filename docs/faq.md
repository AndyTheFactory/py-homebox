# Frequently Asked Questions

## Installation & Setup

### How do I install py-homebox?

```bash
pip install homebox
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add homebox
```

---

### Which version of Homebox is supported?

py-homebox 0.1.0 targets the **Homebox v0.21.0** REST API.
Future Homebox API changes will be tracked in new releases of this library.

---

### Do I need an API token or can I use a username and password?

Both are supported.

**Username / password login:**

```python
from homebox import HomeboxClient

client = HomeboxClient(base_url="https://your-instance/api")
client.login("admin@example.com", "password")
```

**Pre-obtained Bearer token:**

```python
client = HomeboxClient(
    base_url="https://your-instance/api",
    token="your-bearer-token",
)
```

You can also store either value in environment variables (`HOMEBOX_URL`, `HOMEBOX_TOKEN`) and construct the client with no arguments.

---

### What environment variables does py-homebox read?

| Variable          | Required | Description |
|-------------------|----------|-------------|
| `HOMEBOX_URL`     | **Yes**  | Base URL of the Homebox API, e.g. `https://demo.homebox.software/api` |
| `HOMEBOX_TOKEN`   | No       | Pre-obtained Bearer token. Call `client.login()` if not set. |

---

### Can I load credentials from a `.env` file?

Yes. Install [python-dotenv](https://pypi.org/project/python-dotenv/) and call `load_dotenv()` before constructing the client:

```python
from dotenv import load_dotenv
load_dotenv()

from homebox import HomeboxClient
client = HomeboxClient()  # reads HOMEBOX_URL and HOMEBOX_TOKEN from .env
```

---

## Authentication

### My token expired. Do I need to create a new client?

No. Just call `client.login()` again with your credentials.
The client will fetch a new token and update its internal headers automatically.

---

### How do I stay logged in for longer sessions?

Pass `stay_logged_in=True` to `client.login()`:

```python
client.login("admin@example.com", "password", stay_logged_in=True)
```

The Homebox server will issue a longer-lived token.

---

### Does the client support OAuth providers?

You can pass the optional `provider` argument to `login()`:

```python
client.login("user@example.com", "password", provider="oidc")
```

---

## Working with Items

### How do I search for items by name?

```python
result = client.items.query_all_items(q="laptop")
for item in result.items or []:
    print(item.name)
```

---

### How do I filter items by label or location?

```python
result = client.items.query_all_items(
    labels=["label-uuid-1"],
    locations=["location-uuid-1"],
)
```

---

### How do I bulk-import items?

Export a blank CSV to discover the column layout, fill in your rows, then import:

```python
csv_template = client.items.export_items()
# … build your CSV …
client.items.import_items(my_csv_bytes)
```

---

### How do I attach a photo to an item?

```python
with open("photo.jpg", "rb") as f:
    client.items.create_item_attachment(
        "item-uuid",
        file=f.read(),
        type="photo",
        primary=True,
        name="front.jpg",
    )
```

---

### How do I download an attachment?

```python
data = client.items.get_item_attachment("item-uuid", "attachment-uuid")
with open("downloaded.jpg", "wb") as f:
    f.write(data)
```

---

## Locations

### How do I create a nested location hierarchy?

```python
from homebox.models import LocationCreate

office = client.locations.create_location(LocationCreate(name="Office"))
desk   = client.locations.create_location(LocationCreate(name="Desk", parentId=office.id))
drawer = client.locations.create_location(LocationCreate(name="Drawer", parentId=desk.id))
```

---

### How do I get the full location tree?

```python
tree = client.locations.get_locations_tree()
```

---

## Labels

### How do I create and assign a label?

```python
from homebox.models import LabelCreate, ItemUpdate

label = client.labels.create_label(LabelCreate(name="Electronics", color="#0ea5e9"))

# assign the label when creating or updating an item
client.items.update_item("item-uuid", ItemUpdate(labelIds=[label.id]))
```

---

## Maintenance

### How do I log a maintenance event for an item?

```python
from homebox.models import MaintenanceEntryCreate

client.items.create_maintenance_entry(
    "item-uuid",
    MaintenanceEntryCreate(
        name="Annual service",
        scheduledDate="2025-06-01",
        cost="150.00",
    ),
)
```

---

### How do I query upcoming maintenance across all items?

```python
from homebox.models import MaintenanceFilterStatus

scheduled = client.maintenance.query_all_maintenance(
    status=MaintenanceFilterStatus.MaintenanceFilterStatusScheduled
)
```

---

## Statistics & Reporting

### How do I get an overview of my inventory?

```python
stats = client.groups.get_group_statistics()
print(f"Total items: {stats.totalItems}")
print(f"Total value: {stats.totalItemPrice}")
```

---

### How do I export a Bill of Materials?

```python
bom_csv = client.reporting.export_bill_of_materials()
with open("bom.csv", "w") as f:
    f.write(bom_csv)
```

---

## Label Maker & QR Codes

### How do I generate a printable label for an item?

```python
png_bytes = client.labelmaker.get_item_label("item-uuid", print=False)
with open("label.png", "wb") as f:
    f.write(png_bytes)
```

---

### How do I look up a product by barcode?

```python
products = client.products.search_ean_from_barcode("0012345678905")
for product in products:
    print(product.manufacturer, product.modelNumber)
```

---

## Error Handling

### What exceptions can the client raise?

All HTTP errors (4xx, 5xx) are raised as `requests.HTTPError`.
Wrap calls in a try/except block to handle them:

```python
import requests

try:
    item = client.items.get_item("non-existent-uuid")
except requests.HTTPError as exc:
    print(f"API error: {exc.response.status_code} – {exc.response.text}")
```

---

### How do I handle a missing `base_url`?

If neither the `base_url` argument nor the `HOMEBOX_URL` environment variable is set, the constructor raises `ValueError`:

```
ValueError: base_url must be provided or the HOMEBOX_URL environment variable must be set
```

---

## Contributing

### How do I set up a development environment?

```bash
git clone https://github.com/AndyTheFactory/py-homebox
cd py-homebox
uv sync --group dev
pre-commit install
```

Run tests with:

```bash
uv run pytest -m "not real"
```
