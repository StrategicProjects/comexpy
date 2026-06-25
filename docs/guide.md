# User guide

## The three datasets

| Function | Period | Product detail | Metrics |
|----------|--------|----------------|---------|
| `comex_query` / `comex_export` / `comex_import` | 1997–present | NCM, HS2/4/6, CGCE, SITC, ISIC | FOB, KG, statistic, freight, insurance, CIF |
| `comex_query_city` | 1997–present | HS2/HS4 only | FOB, KG |
| `comex_historical` | 1989–1996 | NBM | FOB, KG |

### General trade

```python
comexpy.comex_query(
    flow="export",
    start_period="2023-01",
    end_period="2023-12",
    details=["ncm", "country"],
    filters={"country": [160, 249]},
    month_detail=True,
    metric_cif=True,
)
```

### City-level

City information is based on the **declarant** of exports/imports, not the
producer or buyer. Only FOB and KG metrics are available, and product detail
goes only down to HS4.

```python
comexpy.comex_query_city(
    flow="export",
    start_period="2023-01",
    end_period="2023-12",
    details=["country", "state"],
    filters={"state": 26},
)
```

### Historical (1989–1996)

Uses the NBM nomenclature. Details are limited to `country`, `state` and
`nbm`.

```python
comexpy.comex_historical(
    flow="export",
    start_period="1995-01",
    end_period="1996-12",
    details="country",
)
```

## Detail and filter aliases

The package maps user-friendly names to the API's internal names. You can
always pass the API name verbatim instead.

| Alias | API name |
|-------|----------|
| `bloc` / `economic_block` | `economicBlock` |
| `transport_mode` | `via` |
| `customs_unit` | `urf` |
| `hs6` / `sh6` | `subHeading` |
| `hs4` / `sh4` | `heading` |
| `hs2` / `sh2` | `chapter` |
| `cgce_n1/2/3` | `BECLevel1/2/3` |
| `sitc_section` … | `SITCSection` … |
| `isic_section` … | `ISICSection` … |

The full table is exposed as `comexpy.DETAILS_MAP`.

## Auxiliary tables

```python
# Geography
comexpy.comex_countries()
comexpy.comex_blocs(language="pt")
comexpy.comex_states()
comexpy.comex_cities()
comexpy.comex_transport_modes()
comexpy.comex_customs_units()

# Products
comexpy.comex_ncm(search="animal")
comexpy.comex_nbm()
comexpy.comex_hs(add="ncm")

# Classifications
comexpy.comex_cgce()
comexpy.comex_sitc(search="carne")
comexpy.comex_isic("division")
```

Every `*_detail` function (e.g. `comex_country_detail(105)`) returns a single
record as a `dict`.

## Configuration

```python
comexpy.set_options(
    timeout_get=60,    # seconds, GET requests
    timeout_post=120,  # seconds, POST requests
    max_tries=3,       # attempts per request
    retry_time=10,     # seconds between retries (API recommends 10)
    ssl_verify=True,   # set False to skip ICP-Brasil verification
)
comexpy.set_verbose(False)   # silence progress/success messages
```
