# Get Item Labels

This example shows how to generate printable PNG label files for every item stored in a Homebox location.

## What it demonstrates

- Listing all locations with `client.locations.get_all_locations()`
- Querying items within a specific location with `client.items.query_all_items()`
- Generating a printable label for each item with `client.labelmaker.get_item_label()`
- Saving the binary PNG data to disk

## Setup

Copy `examples/.env.sample` to `examples/.env` and set:

```
HOMEBOX_URL=https://your-homebox-instance/api
HOMEBOX_USERNAME=your@email.com
HOMEBOX_PASSWORD=yourpassword
```

Then run:

```bash
python examples/get_items_label.py
```

One PNG file per item will be saved to the current working directory.

## Source code

```python title="examples/get_items_label.py"
--8<-- "examples/get_items_label.py"
```
