# comexpy

<img src="assets/logo.svg" align="right" height="180" alt="comexpy logo" />

**Access the Brazilian Foreign Trade Statistics API (ComexStat) from Python.**

`comexpy` is a [pandas](https://pandas.pydata.org/)-friendly interface to the
[ComexStat API](https://api-comexstat.mdic.gov.br/docs#/) of the Brazilian
Ministry of Development, Industry, Trade and Services (MDIC). Query detailed
Brazilian export and import data — every fetch returns a `pandas.DataFrame`.

It is the Python port of the R package
[`comexr`](https://github.com/StrategicProjects/comexr); the public function
names mirror the R API so knowledge transfers directly between the two.

## Install

```bash
pip install comexpy
```

## A first query

```python
import comexpy

# Exports by country in January 2024
df = comexpy.comex_export(
    start_period="2024-01",
    end_period="2024-01",
    details="country",
)
```

Continue with the [Getting started](getting-started.md) guide, the
[User guide](guide.md), or jump to the full [API reference](reference.md).

## Highlights

- **Tidy output** — every query and table function returns a
  `pandas.DataFrame`.
- **Three datasets** — general trade (1997–present), city-level, and
  historical (1989–1996).
- **Friendly aliases** — pass `"hs4"`, `"transport_mode"`, `"cgce_n1"`; the
  package translates them to the API's internal names.
- **Resilient HTTP** — configurable retry/timeout for the API's aggressive
  rate limiting, plus SSL auto-fallback for ICP-Brasil certificates.
