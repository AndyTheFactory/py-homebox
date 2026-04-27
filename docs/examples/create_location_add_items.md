# Create Location and Add Items

This example demonstrates how to create a new storage location in Homebox, add items to it (both individually and in bulk via CSV import), attach images, and generate a printable location label.

## What it demonstrates

- Creating a location with `client.locations.create_location()`
- Creating a single item with `client.items.create_item()`
- Uploading photo attachments with `client.items.create_item_attachment()`
- Bulk-importing items from CSV using `client.items.export_items()` and `client.items.import_items()`
- Generating a printable PNG label for a location with `client.labelmaker.get_location_label()`

## Setup

Copy `examples/.env.sample` to `examples/.env` and set:

```
HOMEBOX_URL=https://your-homebox-instance/api
HOMEBOX_USERNAME=your@email.com
HOMEBOX_PASSWORD=yourpassword
```

Then run:

```bash
python examples/create_location_add_items.py
```

A PNG label file will be saved to the current working directory.

## Source code

```python title="examples/create_location_add_items.py"
--8<-- "examples/create_location_add_items.py"
```
