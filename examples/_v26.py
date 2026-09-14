"""Shared helpers for Homebox v0.26 entity examples."""

from homebox import HomeboxClient
from homebox.models import EntityOut, EntityTypeSummary, TreeItem


def require_entity_type(client: HomeboxClient, *, is_location: bool) -> EntityTypeSummary:
    """Return the first entity type matching the requested location behavior."""
    entity_type = next(
        (
            candidate
            for candidate in client.entity_types.get_all_entity_types()
            if candidate.isLocation is is_location and candidate.id
        ),
        None,
    )
    if entity_type is None:
        kind = "location" if is_location else "item"
        raise RuntimeError(f"No {kind} entity type found. Create one in Homebox before running this example.")
    return entity_type


def require_id(value: str | None, *, resource: str) -> str:
    """Return a response ID or fail before using an invalid follow-up request."""
    if value is None:
        raise RuntimeError(f"{resource} was created but no id was returned")
    return value


def get_location_entities(client: HomeboxClient) -> list[EntityOut]:
    """Return location-like entities by traversing the v0.26 entity tree."""
    locations: list[EntityOut] = []

    def visit(node: TreeItem) -> int:
        item_count = 0
        for child in node.children or []:
            if child.type == "location":
                item_count += visit(child)
            else:
                item_count += 1
        if node.type == "location":
            locations.append(EntityOut(id=node.id, name=node.name, itemCount=item_count))
        return item_count

    for root in client.entities.get_entities_tree(withItems=True):
        visit(root)
    return locations
