
# Homebox API

A Python wrapper for the Homebox API.

## Installation

```bash
pip install homebox-api
```

## Usage

### Explicit credentials

```python
from homebox import HomeboxClient

client = HomeboxClient(base_url="https://demo.homebox.software/api", token="your-token")
```

### Environment variables

You can configure the client through environment variables so credentials are never hardcoded:

| Variable        | Description                                  |
|-----------------|----------------------------------------------|
| `HOMEBOX_URL`   | Base URL of the Homebox API (required)       |
| `HOMEBOX_TOKEN` | Bearer token for pre-authenticated requests  |

```bash
export HOMEBOX_URL="https://demo.homebox.software/api"
export HOMEBOX_TOKEN="your-token"  # optional, can log in instead
```

```python
from homebox import HomeboxClient

# reads HOMEBOX_URL and HOMEBOX_TOKEN from the environment
client = HomeboxClient()
```

Explicit arguments always take precedence over environment variables.

### Authentication via login

If you don't have a token yet, log in with username and password:

```python
client = HomeboxClient(base_url="https://demo.homebox.software/api")
client.login("admin@admin.com", "admin")

# subsequent calls now carry the Bearer token automatically
items = client.items.query_all_items()
print(items)
```
