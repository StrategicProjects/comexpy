"""City-level foreign trade data queries (POST ``/cities``)."""
from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union

import pandas as pd

from . import _msg
from ._client import comex_post
from ._format import (
    build_details,
    build_filters,
    convert_flow,
    response_to_df,
    validate_period,
)

Details = Union[str, Sequence[str], None]
Filters = Optional[Mapping[str, Any]]


def comex_query_city(
    flow: str = "export",
    start_period: str = None,
    end_period: str = None,
    details: Details = None,
    filters: Filters = None,
    month_detail: bool = True,
    metric_fob: bool = True,
    metric_kg: bool = True,
    language: str = "en",
    verbose: bool = True,
) -> pd.DataFrame:
    """Query city-level Brazilian foreign trade data.

    City-level data is more aggregated than general data, with fewer
    available details and metrics. City information is based on the declarant
    of exports/imports, not the producer or buyer.

    Parameters
    ----------
    flow : str
        Trade flow: ``"export"`` or ``"import"``.
    start_period, end_period : str
        Period bounds in ``"YYYY-MM"`` format.
    details : str or sequence of str, optional
        Detail/grouping fields. The city endpoint accepts only a subset of
        the general fields:

        * **Geographic:** ``"country"``, ``"bloc"`` (``"economic_block"``),
          ``"state"``, ``"city"``
        * **Products:** ``"hs4"``/``"sh4"`` (API ``heading``),
          ``"hs2"``/``"sh2"`` (API ``chapter``), ``"section"``
    filters : mapping, optional
        Mapping of filter name to value(s). Accepts the same names as
        ``details``. Example: ``{"city": "3550308", "state": "26"}``.
    month_detail : bool
        If ``True`` (default), break down results by month.
    metric_fob, metric_kg : bool
        Only FOB (US$) and net weight (kg) are supported at city level.
    language : str
        Response language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    verbose : bool
        Show progress messages (default ``True``).

    Returns
    -------
    pandas.DataFrame
        The query results.

    Notes
    -----
    City-level data differs from general data: full NCM and HS6 are not
    available (product detail goes only to HS4); CGCE, SITC and ISIC are not
    available; transport mode and customs unit are not available; and only
    FOB and KG metrics are supported.
    """
    validate_period(start_period, end_period)
    flow_api = convert_flow(flow)

    if verbose:
        label = "exports" if flow_api == "export" else "imports"
        _msg.info(
            f"Querying city-level {label} from {start_period} to {end_period}"
        )

    metrics = []
    if metric_fob:
        metrics.append("metricFOB")
    if metric_kg:
        metrics.append("metricKG")
    if not metrics:
        raise ValueError(
            "At least one metric must be selected (metric_fob or metric_kg)."
        )

    body = {
        "flow": flow_api,
        "monthDetail": month_detail,
        "period": {"from": start_period, "to": end_period},
        "filters": build_filters(filters),
        "details": build_details(details),
        "metrics": metrics,
    }

    data = comex_post("/cities", body, query={"language": language}, verbose=verbose)
    result = response_to_df(data)

    if verbose and len(result) > 0:
        _msg.success(f"{len(result)} records found")

    return result
