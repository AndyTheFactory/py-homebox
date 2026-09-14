from examples._v26 import get_location_entities
from homebox.client import HomeboxClient
from homebox.models import TreeItem


def test_location_discovery_uses_v26_tree(mocker):
    client = HomeboxClient(base_url="http://localhost:8080")
    tree = [
        TreeItem(
            id="building",
            name="Building",
            type="location",
            children=[
                TreeItem(
                    id="office",
                    name="Office",
                    type="location",
                    children=[TreeItem(id="laptop", name="Laptop", type="item")],
                ),
                TreeItem(id="camera", name="Camera", type="item"),
            ],
        )
    ]
    get_tree = mocker.patch.object(client.entities, "get_entities_tree", return_value=tree)

    locations = get_location_entities(client)

    assert [(location.id, location.itemCount) for location in locations] == [("office", 1), ("building", 2)]
    get_tree.assert_called_once_with(withItems=True)
