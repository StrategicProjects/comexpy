# comexpy

[![PyPI](https://img.shields.io/pypi/v/comexpy.svg)](https://pypi.org/project/comexpy/)
[![Python versions](https://img.shields.io/pypi/pyversions/comexpy.svg)](https://pypi.org/project/comexpy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Access the Brazilian Foreign Trade Statistics API (ComexStat) from Python.**

`comexpy` is a pandas-friendly interface to the
[ComexStat API](https://api-comexstat.mdic.gov.br/docs#/) of the Brazilian
Ministry of Development, Industry, Trade and Services (MDIC). It provides
programmatic access to detailed Brazilian export and import data — every
query returns a `pandas.DataFrame`.

This is the Python port of the R package
[`comexr`](https://github.com/StrategicProjects/comexr); the public function
names mirror the R API so knowledge transfers directly between the two.

## Features

- **General trade data** (1997–present), **city-level** data, and
  **historical** records (1989–1996)
- **Auxiliary tables**: countries, economic blocs, NCM/NBM/HS product codes,
  CGCE/SITC/ISIC classifications, states, cities, transport modes, customs units
- **Friendly aliases** — pass `"hs4"`, `"transport_mode"`, `"cgce_n1"` and the
  package translates them to the API's internal names
- **Multilingual** responses: Portuguese, English, Spanish
- **SSL auto-fallback** — handles ICP-Brasil certificate issues transparently
- **Configurable retry/timeout** for the API's aggressive rate limiting

## Installation

```bash
pip install comexpy
```

Requires Python 3.9+, `requests` and `pandas`.

## Quick start

```python
import comexpy

# Exports by country in January 2024
exports = comexpy.comex_export(
    start_period="2024-01",
    end_period="2024-01",
    details="country",
)

# Imports with CIF value, by country, for all of 2024
imports = comexpy.comex_import(
    start_period="2024-01",
    end_period="2024-12",
    details="country",
    metric_cif=True,
)

# Exports to China (160), grouped by HS4
# (the package translates "hs4" to the API's `heading`)
soy = comexpy.comex_export(
    start_period="2024-01",
    end_period="2024-12",
    details=["country", "hs4"],
    filters={"country": 160},
)
```

## Discover available options

```python
comexpy.comex_details("general")     # grouping fields available
comexpy.comex_filters("general")     # filters available
comexpy.comex_metrics("general")     # metrics available

# Look up country codes
countries = comexpy.comex_countries()
countries[countries["text"].str.contains("China", case=False)]

# Economic blocs in Portuguese
comexpy.comex_blocs(language="pt")
```

## City-level and historical data

```python
# Exports declared in Pernambuco (state 26) in 2023
comexpy.comex_query_city(
    flow="export",
    start_period="2023-01",
    end_period="2023-12",
    details=["country", "state"],
    filters={"state": 26},
)

# Historical exports 1995–1996 by country (NBM classification)
comexpy.comex_historical(
    flow="export",
    start_period="1995-01",
    end_period="1996-12",
    details="country",
)
```

## Rate limiting and timeouts

The ComexStat API frequently returns rate-limit errors (HTTP 429,
*"Você excedeu o limite de solicitações..."*) or times out. Adjust the
behaviour with `set_options`:

```python
comexpy.set_options(retry_time=30)   # wait 30s between retries
comexpy.set_options(max_tries=5, timeout_post=180)
```

Silence progress/success messages with `comexpy.set_verbose(False)`.

## Public API

| Function | Purpose |
|----------|---------|
| `comex_query` / `comex_export` / `comex_import` | General trade data (1997–present) |
| `comex_query_city` | City-level data |
| `comex_historical` | Historical data (1989–1996) |
| `comex_last_update` / `comex_available_years` | API metadata |
| `comex_filters` / `comex_filter_values` / `comex_details` / `comex_metrics` | Query option discovery |
| `comex_countries` / `comex_blocs` / `comex_states` / `comex_cities` / `comex_transport_modes` / `comex_customs_units` (+ `_detail`) | Geography tables |
| `comex_ncm` / `comex_nbm` / `comex_hs` (+ `_detail`) | Product nomenclatures |
| `comex_cgce` / `comex_sitc` / `comex_isic` | Economic classifications |
| `set_options` / `set_verbose` | Configuration |

## License

MIT — see [LICENSE](LICENSE). Developed by the comexpy authors.
