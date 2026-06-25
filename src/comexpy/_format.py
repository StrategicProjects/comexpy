"""Response conversion, validation and name mappings.

Ported from the R package's ``utils.R``:

* :func:`response_to_df` / :func:`extract_single` handle the ComexStat
  response shapes empirically observed across endpoints.
* :func:`validate_period` / :func:`convert_flow` validate user arguments.
* :data:`DETAILS_MAP` translates user-friendly aliases (``hs4``,
  ``transport_mode``, ``cgce_n1``, …) to the API's internal names
  (``heading``, ``via``, ``BECLevel1``, …).
"""
from __future__ import annotations

import re
from typing import Any, Mapping, Optional

import pandas as pd

# -------------------------------------------------------------------------
# Response conversion
# -------------------------------------------------------------------------


def _flatten_value(val: Any) -> Any:
    """Collapse nested lists to a comma-joined string; keep scalars as-is."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        return ", ".join(str(v) for v in val)
    if isinstance(val, dict):
        return ", ".join(str(v) for v in val.values())
    return val


def response_to_df(response: Any, path: str = "data") -> pd.DataFrame:
    """Convert a ComexStat API response into a :class:`pandas.DataFrame`.

    Handles every known response pattern:

    * ``{"data": {"list": [...rows...], "count": N}}`` — most endpoints,
      including POST ``/general`` and ``/cities``.
    * ``{"data": [...rows...]}`` — ``/tables/uf``, ``/tables/cities``,
      ``/tables/ways``, ``/tables/urf``, POST ``/historical-data/``.
    * ``{"data": [[...rows...]]}`` — ``/general/filters/{filter}``.
    """
    data: Any = response
    if isinstance(response, Mapping) and path in response:
        data = response[path]

    if data is None:
        return pd.DataFrame()

    # Pattern 1: {"list": [...], "count": N}
    if isinstance(data, Mapping) and "list" in data:
        data = data["list"]

    if data is None:
        return pd.DataFrame()

    # Pattern 3: unwrap single-element unnamed lists wrapping the rows.
    while (
        isinstance(data, (list, tuple))
        and len(data) == 1
        and isinstance(data[0], (list, tuple))
    ):
        data = data[0]

    if isinstance(data, (list, tuple)):
        if len(data) == 0:
            return pd.DataFrame()
        rows = [
            {k: _flatten_value(v) for k, v in row.items()}
            if isinstance(row, Mapping)
            else {"value": _flatten_value(row)}
            for row in data
        ]
        return pd.DataFrame(rows)

    # Named object that is not a list of rows -> single-row frame.
    if isinstance(data, Mapping):
        return pd.DataFrame([{k: _flatten_value(v) for k, v in data.items()}])

    return pd.DataFrame()


def extract_single(response: Any) -> Any:
    """Extract a single record (dict/scalar) from a detail-endpoint response.

    Handles ``{"data": {...}}``, ``{"data": [{...}]}``,
    ``{"data": {"list": [{...}]}}`` and ``{"data": null}``.
    """
    if not isinstance(response, Mapping):
        return None
    data = response.get("data")
    if data is None:
        return None

    if isinstance(data, Mapping) and "list" in data:
        lst = data["list"]
        if not lst:
            return None
        return lst[0]

    if isinstance(data, (list, tuple)):
        if len(data) == 0:
            return None
        return data[0]

    return data


# -------------------------------------------------------------------------
# Validation
# -------------------------------------------------------------------------

_PERIOD_RE = re.compile(r"^\d{4}-\d{2}$")


def validate_period(start_period: str, end_period: str) -> None:
    """Validate ``YYYY-MM`` period strings and their ordering."""
    if not _PERIOD_RE.match(str(start_period)):
        raise ValueError(
            f"Invalid start period: {start_period}. "
            "Use format 'YYYY-MM' (e.g. '2023-01')."
        )
    if not _PERIOD_RE.match(str(end_period)):
        raise ValueError(
            f"Invalid end period: {end_period}. "
            "Use format 'YYYY-MM' (e.g. '2023-12')."
        )
    if start_period > end_period:
        raise ValueError("Start period must be before or equal to end period.")


def convert_flow(flow: str) -> str:
    """Normalise a trade-flow argument to ``"export"`` or ``"import"``."""
    fl = str(flow).lower()
    if fl in ("exp", "export", "exports"):
        return "export"
    if fl in ("imp", "import", "imports"):
        return "import"
    raise ValueError(f"Invalid flow: {flow}. Use 'export' or 'import'.")


# -------------------------------------------------------------------------
# Name mappings (user-friendly -> API names)
# -------------------------------------------------------------------------

#: Verified against the live endpoints (/general/filters, /general/details,
#: /cities/filters, /historical-data/filters). The map also maps every API
#: name to itself, so callers who already know the API name may pass it
#: verbatim.
DETAILS_MAP = {
    # Geographic
    "country": "country",
    "bloc": "economicBlock",
    "economic_block": "economicBlock",
    "economicBlock": "economicBlock",
    "state": "state",
    "city": "city",
    "transport_mode": "via",
    "via": "via",
    "customs_unit": "urf",
    "urf": "urf",
    # Products - NCM and Harmonized System (HS2/HS4/HS6)
    "ncm": "ncm",
    "hs6": "subHeading",
    "sh6": "subHeading",
    "subheading": "subHeading",
    "subHeading": "subHeading",
    "hs4": "heading",
    "sh4": "heading",
    "heading": "heading",
    "hs2": "chapter",
    "sh2": "chapter",
    "chapter": "chapter",
    "section": "section",
    # CGCE (a.k.a. BEC - Broad Economic Categories)
    "cgce_n1": "BECLevel1",
    "cgce_n2": "BECLevel2",
    "cgce_n3": "BECLevel3",
    "BECLevel1": "BECLevel1",
    "BECLevel2": "BECLevel2",
    "BECLevel3": "BECLevel3",
    # SITC / CUCI
    "sitc_section": "SITCSection",
    "sitc_division": "SITCDivision",
    "sitc_chapter": "SITCDivision",
    "sitc_group": "SITCGroup",
    "sitc_position": "SITCGroup",
    "sitc_subgroup": "SITCSubGroup",
    "sitc_subposition": "SITCSubGroup",
    "sitc_basic_heading": "SITCBasicHeading",
    "sitc_item": "SITCBasicHeading",
    "SITCSection": "SITCSection",
    "SITCDivision": "SITCDivision",
    "SITCGroup": "SITCGroup",
    "SITCSubGroup": "SITCSubGroup",
    "SITCBasicHeading": "SITCBasicHeading",
    # ISIC
    "isic_section": "ISICSection",
    "isic_division": "ISICDivision",
    "isic_group": "ISICGroup",
    "isic_class": "ISICClass",
    "ISICSection": "ISICSection",
    "ISICDivision": "ISICDivision",
    "ISICGroup": "ISICGroup",
    "ISICClass": "ISICClass",
    # NBM (historical)
    "nbm": "nbm",
}

_API_NAMES = set(DETAILS_MAP.values())


def get_api_name(name: str) -> str:
    """Translate a user-friendly detail/filter alias to its API name."""
    if name in DETAILS_MAP:
        return DETAILS_MAP[name]
    if name in _API_NAMES:
        return name
    from . import _msg

    _msg.warn(f"Unknown detail/filter: {name}. Will be sent as-is.")
    return name


def _as_list(x: Any) -> list:
    if x is None:
        return []
    if isinstance(x, (list, tuple, set)):
        return list(x)
    return [x]


def build_details(details: Any) -> list:
    """Build the API ``details`` list from user aliases."""
    return [get_api_name(d) for d in _as_list(details)]


def build_filters(filters: Optional[Mapping[str, Any]]) -> list:
    """Build the API ``filters`` list from a name -> values mapping."""
    if not filters:
        return []
    return [
        {"filter": get_api_name(name), "values": _as_list(values)}
        for name, values in filters.items()
    ]


def build_metrics(
    metric_fob: bool = True,
    metric_kg: bool = True,
    metric_statistic: bool = False,
    metric_freight: bool = False,
    metric_insurance: bool = False,
    metric_cif: bool = False,
) -> list:
    """Build the API ``metrics`` list from the metric flags."""
    metrics = []
    if metric_fob:
        metrics.append("metricFOB")
    if metric_kg:
        metrics.append("metricKG")
    if metric_statistic:
        metrics.append("metricStatistic")
    if metric_freight:
        metrics.append("metricFreight")
    if metric_insurance:
        metrics.append("metricInsurance")
    if metric_cif:
        metrics.append("metricCIF")
    if not metrics:
        raise ValueError("At least one metric must be selected.")
    return metrics
