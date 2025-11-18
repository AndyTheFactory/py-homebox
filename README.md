
# Homebox API

A Python wrapper for the Homebox API.

## Installation

```bash
pip install homebox-api
```

## Usage

```python
from homebox import HomeboxClient

client = HomeboxClient(base_url="https://demo.homebox.software/api", token="your-token")

# Get all items
items = client.query_all_items()

print(items)
```
