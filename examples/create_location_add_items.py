"""Example script that shows how to create a new location in homebox and add several items to that location.

Exemplifies how to add images to items, and how to use the bulk item creation endpoint.
Script generates a label png for the created location.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost
- HOMEBOX_USERNAME: the username of a user with permissions to create locations and items
- HOMEBOX_PASSWORD: the password of that user

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import base64
import csv
import io
import os
from datetime import UTC, datetime
from pathlib import Path

from homebox import HomeboxClient
from homebox.models import ItemCreate, LocationCreate


def _load_dotenv() -> None:
    dotenv_path = Path(__file__).parent / ".env"
    if not dotenv_path.is_file():
        return

    with dotenv_path.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _build_client() -> HomeboxClient:
    base_url = _require_env("HOMEBOX_URL")
    username = _require_env("HOMEBOX_USERNAME")
    password = _require_env("HOMEBOX_PASSWORD")

    client = HomeboxClient(base_url=base_url)
    client.login(username, password)
    return client


def _tiny_png() -> bytes:
    return base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7+X0kAAAAASUVORK5CYII="
    )


def _safe_name(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    return cleaned or "location"


def _set_first_key(record: dict[str, str], keys: list[str], value: str) -> None:
    lowered = {k.lower().replace(" ", ""): k for k in record}
    for key in keys:
        match = lowered.get(key.lower().replace(" ", ""))
        if match:
            record[match] = value
            return


def main() -> None:
    _load_dotenv()
    client = _build_client()

    location_name = f"Example Storage {datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    location = client.locations.create_location(
        LocationCreate(
            name=location_name,
            description="Location created by create_location_add_items.py",
        )
    )
    print(f"Created location: {location.name} ({location.id})")

    featured_item = client.items.create_item(
        ItemCreate(
            name="Mirrorless Camera",
            description="Featured item created individually",
            quantity=1,
            locationId=location.id,
        )
    )
    print(f"Created featured item: {featured_item.name} ({featured_item.id})")

    image = _tiny_png()
    client.items.create_item_attachment(
        featured_item.id,
        file=image,
        type="photo",
        primary=True,
        name="front.png",
    )
    client.items.create_item_attachment(
        featured_item.id,
        file=image,
        type="photo",
        primary=False,
        name="rear.png",
    )
    print("Attached two images to the featured item")

    bulk_items = [
        {"name": "Tripod", "description": "Carbon tripod", "quantity": "1"},
        {"name": "Camera Bag", "description": "Weather resistant bag", "quantity": "2"},
        {"name": "SD Card", "description": "128GB UHS-II", "quantity": "4"},
    ]

    exported_csv = client.items.export_items()
    headers = next(csv.reader([exported_csv.splitlines()[0]]))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=headers)
    writer.writeheader()
    for item in bulk_items:
        row = {header: "" for header in headers}
        _set_first_key(row, ["HB.name"], item["name"])
        _set_first_key(row, ["HB.description"], item["description"])
        _set_first_key(row, ["HB.quantity", "HB.qty"], item["quantity"])
        _set_first_key(row, ["HB.location", "HB.locationname"], location.name)
        writer.writerow(row)
    client.items.import_items(out.getvalue().encode("utf-8"))
    print(f"Bulk-created {len(bulk_items)} items using import_items()")

    label_data = client.labelmaker.get_location_label(location.id, print=False)
    output_file = Path.cwd() / f"{_safe_name(location_name)}_label.png"
    output_file.write_bytes(label_data)
    print(f"Saved location label to: {output_file}")


if __name__ == "__main__":
    main()
