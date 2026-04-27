# Item Attachments

This example shows how to upload, list, and download file attachments on a Homebox item.

## What it demonstrates

- Creating a temporary location and item
- Uploading a text file attachment (`type="manual"`) with `client.items.create_item_attachment()`
- Uploading a photo attachment (`type="photo"`) with `client.items.create_item_attachment()`
- Retrieving attachment metadata from `client.items.get_item()`
- Downloading raw attachment bytes with `client.items.get_item_attachment()`

## Setup

Copy `examples/.env.sample` to `examples/.env` and set:

```
HOMEBOX_URL=https://your-homebox-instance/api
HOMEBOX_USERNAME=your@email.com
HOMEBOX_PASSWORD=yourpassword
```

Then run:

```bash
python examples/item_attachements.py
```

The downloaded attachment will be saved to the current working directory.

## Source code

```python title="examples/item_attachements.py"
--8<-- "examples/item_attachements.py"
```
