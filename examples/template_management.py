"""Example script that shows how to manage item templates in Homebox.

Script demonstrates how to create, update, and delete item templates.

In order to run this script, you need to have the following environment variables set:
- HOMEBOX_URL: the URL of your Homebox instance (e.g. http://localhost
- HOMEBOX_USERNAME: the username of a user with permissions to create locations and items
- HOMEBOX_PASSWORD: the password of that user

You can use the .env.sample file in the examples directory as a template for your .env file.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from homebox import HomeboxClient
from homebox.models import (
    ItemTemplateCreate,
    ItemTemplateCreateItemRequest,
    ItemTemplateUpdate,
    LabelCreate,
    LocationCreate,
    TemplateField,
)


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


def main() -> None:
    _load_dotenv()
    client = _build_client()

    created_template_id: str | None = None
    created_item_id: str | None = None
    created_location_id: str | None = None
    created_label_id: str | None = None

    ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    try:
        before = client.templates.get_all_templates()
        print(f"Templates before create: {len(before)}")

        location = client.locations.create_location(
            LocationCreate(
                name=f"Template Example Shelf {ts}",
                description="Location used by template_management.py",
            )
        )
        created_location_id = location.id
        print(f"Created location: {location.name} ({location.id})")

        label = client.labels.create_label(
            LabelCreate(
                name=f"TemplateExample{ts}",
                color="#22c55e",
                description="Label used by template_management.py",
            )
        )
        created_label_id = label.id
        print(f"Created label: {label.name} ({label.id})")

        template = client.templates.create_template(
            ItemTemplateCreate(
                name=f"Laptop Template {ts}",
                description="Reusable template for laptop assets",
                notes="Created by template_management.py",
                defaultName="Work Laptop",
                defaultDescription="Company-managed laptop",
                defaultManufacturer="Lenovo",
                defaultModelNumber="ThinkPad T14",
                defaultQuantity=1,
                defaultInsured=True,
                defaultLifetimeWarranty=False,
                defaultWarrantyDetails="36 months standard warranty",
                defaultLabelIds=[label.id],
                defaultLocationId=location.id,
                includePurchaseFields=True,
                includeWarrantyFields=True,
                includeSoldFields=False,
                fields=[TemplateField(name="Asset Owner", type="text", textValue="IT Department")],
            )
        )
        created_template_id = template.id
        print(f"Created template: {template.name} ({template.id})")

        fetched = client.templates.get_template(template.id)
        print(f"Fetched template: {fetched.name}, defaults -> manufacturer={fetched.defaultManufacturer}")

        updated = client.templates.update_template(
            template.id,
            ItemTemplateUpdate(
                id=template.id,
                name=f"Laptop Template {ts} v2",
                description="Updated reusable template for laptop assets",
                notes="Updated by template_management.py",
                defaultName="Developer Laptop",
                defaultDescription="Template-backed laptop item",
                defaultManufacturer="Lenovo",
                defaultModelNumber="ThinkPad T14 Gen 5",
                defaultQuantity=1,
                defaultInsured=True,
                defaultLifetimeWarranty=False,
                defaultWarrantyDetails="36 months onsite warranty",
                defaultLabelIds=[label.id],
                defaultLocationId=location.id,
                includePurchaseFields=True,
                includeWarrantyFields=True,
                includeSoldFields=False,
                fields=[TemplateField(name="Asset Owner", type="text", textValue="Engineering")],
            ),
        )
        print(f"Updated template name: {updated.name}")

        created_item = client.templates.create_item_from_template(
            template.id,
            ItemTemplateCreateItemRequest(
                name=f"Template-Created Laptop {ts}",
                locationId=location.id,
                labelIds=[label.id],
                description="Item created using template endpoint",
                quantity=1,
            ),
        )
        created_item_id = created_item.id
        print(f"Created item from template: {created_item.name} ({created_item.id})")

        after = client.templates.get_all_templates()
        print(f"Templates after create/update: {len(after)}")

    finally:
        if created_item_id:
            client.items.delete_item(created_item_id)
            print(f"Deleted created item: {created_item_id}")

        if created_template_id:
            client.templates.delete_template(created_template_id)
            print(f"Deleted created template: {created_template_id}")

        if created_label_id:
            client.labels.delete_label(created_label_id)
            print(f"Deleted created label: {created_label_id}")

        if created_location_id:
            client.locations.delete_location(created_location_id)
            print(f"Deleted created location: {created_location_id}")


if __name__ == "__main__":
    main()
