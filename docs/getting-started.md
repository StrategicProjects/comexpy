# Getting started

## Install

```bash
pip install comexpy
```

Requires Python 3.9+, `requests` and `pandas`.

## Your first queries

```python
import comexpy

# Exports by country in January 2024 (monthly detail off → one row per country)
exports = comexpy.comex_export(
    start_period="2024-01",
    end_period="2024-01",
    details="country",
    month_detail=False,
)

# Imports for all of 2024, by country, including the CIF value
imports = comexpy.comex_import(
    start_period="2024-01",
    end_period="2024-12",
    details="country",
    metric_cif=True,
)
```

## Filtering and grouping

`details` controls the grouping; `filters` restricts the rows. Both accept
friendly aliases that the package translates to the API's internal names
(e.g. `"hs4"` → `heading`, `"transport_mode"` → `via`).

```python
# Exports to China (160), grouped by HS4 product heading
soy = comexpy.comex_export(
    start_period="2024-01",
    end_period="2024-12",
    details=["country", "hs4"],
    filters={"country": 160},
)
```

## Discover what you can query

```python
comexpy.comex_details("general")   # available grouping fields
comexpy.comex_filters("general")   # available filters
comexpy.comex_metrics("general")   # available metrics

# Look up codes
comexpy.comex_countries(search="china")
comexpy.comex_ncm(search="soja", per_page=10)
```

## Messages and rate limiting

The ComexStat API rate-limits aggressively. Tune the HTTP behaviour and
silence progress messages as needed:

```python
comexpy.set_options(retry_time=30, max_tries=5)
comexpy.set_verbose(False)
```
