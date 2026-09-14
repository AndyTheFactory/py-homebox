"""Example script that creates location-like and item-like entities in Homebox.

It demonstrates attachments, duplication, CSV entity import/export, and labels.
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

from _v26 import require_entity_type, require_id

from homebox import HomeboxClient
from homebox.models import DuplicateOptions, EntityCreate


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
    location_type = require_entity_type(client, is_location=True)
    item_type = require_entity_type(client, is_location=False)

    created_location_id: str | None = None
    created_item_ids: list[str] = []

    location_name = f"Example Storage {datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

    try:
        location = client.entities.create_entity(
            EntityCreate(
                name=location_name,
                description="Location created by create_location_add_items.py",
                entityTypeId=location_type.id,
            )
        )
        created_location_id = require_id(location.id, resource="Location entity")
        location_name = location.name or location_name
        print(f"Created location: {location.name} ({location.id})")

        featured_item = client.entities.create_entity(
            EntityCreate(
                name="Mirrorless Camera",
                description="Featured item created individually",
                entityTypeId=item_type.id,
                quantity=1,
                parentId=created_location_id,
            )
        )
        featured_item_id = require_id(featured_item.id, resource="Featured entity")
        created_item_ids.append(featured_item_id)
        print(f"Created featured item: {featured_item.name} ({featured_item.id})")

        image = _tiny_png()
        client.entities.create_attachment(
            featured_item_id,
            file=image,
            type="photo",
            primary=True,
            name="front.png",
        )
        client.entities.create_attachment(
            featured_item_id,
            file=image,
            type="photo",
            primary=False,
            name="rear.png",
        )
        print("Attached two images to the featured item")

        # Show the ancestry path of the featured item (location → item).
        path = client.entities.get_entity_path(featured_item_id)
        print("Item path:")
        for node in path:
            node_type = node.type.value if node.type else "unknown"
            print(f"  [{node_type}] {node.name} ({node.id})")

        # Duplicate the featured item and keep track of the copy for cleanup.
        duplicate = client.entities.duplicate_entity(
            featured_item_id,
            DuplicateOptions(
                copyAttachments=True,
                copyCustomFields=True,
                copyMaintenance=False,
                copyPrefix="Copy of ",
            ),
        )
        if duplicate.id:
            created_item_ids.append(duplicate.id)
        print(f"Duplicated item: {duplicate.name} ({duplicate.id})")

        bulk_items = [
            {"name": "Tripod", "description": "Carbon tripod", "quantity": "1"},
            {"name": "Camera Bag", "description": "Weather resistant bag", "quantity": "2"},
            {"name": "SD Card", "description": "128GB UHS-II", "quantity": "4"},
        ]

        exported_csv = client.entities.export_entities()
        headers = next(csv.reader([exported_csv.splitlines()[0]]))
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=headers)
        writer.writeheader()
        for item in bulk_items:
            row = {header: "" for header in headers}
            _set_first_key(row, ["HB.name"], item["name"])
            _set_first_key(row, ["HB.description"], item["description"])
            _set_first_key(row, ["HB.quantity", "HB.qty"], item["quantity"])
            _set_first_key(row, ["HB.location", "HB.locationname"], location_name)
            writer.writerow(row)
        client.entities.import_entities(out.getvalue().encode("utf-8"))
        print(f"Bulk-created {len(bulk_items)} entities using import_entities()")

        label_data = client.labelmaker.get_location_label(created_location_id, print=False)
        output_file = Path.cwd() / f"{_safe_name(location_name)}_label.png"
        output_file.write_bytes(label_data)
        print(f"Saved location label to: {output_file}")

    finally:
        for item_id in created_item_ids:
            client.entities.delete_entity(item_id)
            print(f"Deleted entity: {item_id}")

        if created_location_id:
            client.entities.delete_entity(created_location_id)
            print(f"Deleted location: {created_location_id}")


if __name__ == "__main__":
    main()
