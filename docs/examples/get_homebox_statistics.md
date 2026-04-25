# Get Homebox Statistics

This example shows how to retrieve various aggregate statistics from a Homebox instance and print them to the console.

## What it demonstrates

- Connecting to a Homebox API using username/password login
- Fetching application info (`client.application_info()`)
- Fetching group-level totals via `client.groups.get_group_statistics()`
- Breaking down item values by label (`client.groups.get_label_statistics()`)
- Breaking down item values by location (`client.groups.get_location_statistics()`)
- Querying a purchase-price time series for a date range (`client.groups.get_purchase_price_statistics()`)

## Setup

Copy `examples/.env.sample` to `examples/.env` and set:

```
HOMEBOX_URL=https://your-homebox-instance/api
HOMEBOX_USERNAME=your@email.com
HOMEBOX_PASSWORD=yourpassword
```

Then run:

```bash
python examples/get_homebox_statistics.py
```

## Source code

```python title="examples/get_homebox_statistics.py"
--8<-- "examples/get_homebox_statistics.py"
```
