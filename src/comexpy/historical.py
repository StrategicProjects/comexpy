"""Historical foreign trade data queries (POST ``/historical-data/``)."""
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


def comex_historical(
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
    """Query historical Brazilian foreign trade data (1989-1996).

    Retrieves export and import data from before the SISCOMEX system was
    implemented. Historical data uses the NBM (Brazilian Nomenclature of
    Goods) classification.

    Parameters
    ----------
    flow : str
        Trade flow: ``"export"`` or ``"import"``.
    start_period, end_period : str
        Period bounds in ``"YYYY-MM"`` format (e.g. ``"1990-01"``).
    details : str or sequence of str, optional
        Detail/grouping fields. The historical endpoint supports only:
        ``"country"``, ``"bloc"`` (``"economic_block"``), ``"state"``,
        ``"nbm"``.
    filters : mapping, optional
        Mapping of filter name to value(s). Accepts the same names as
        ``details``.
    month_detail : bool
        If ``True`` (default), break down results by month.
    metric_fob, metric_kg : bool
        Only FOB (US$) and net weight (kg) are supported.
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
    Historical data is available for **1989 to 1996** only, with limited
    details (``"country"``, ``"state"``, ``"nbm"``), NBM (not NCM) product
    classification, and only FOB and KG metrics.
    """
    validate_period(start_period, end_period)
    flow_api = convert_flow(flow)

    start_year = int(str(start_period)[:4])
    end_year = int(str(end_period)[:4])
    if start_year < 1989 or end_year > 1996:
        _msg.warn(
            "Historical data is available from 1989 to 1996. "
            f"Requested period: {start_period} to {end_period}"
        )

    if verbose:
        label = "exports" if flow_api == "export" else "imports"
        _msg.info(
            f"Querying historical {label} from {start_period} to {end_period}"
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

    # The API spec defines this endpoint with a trailing slash.
    data = comex_post(
        "/historical-data/", body, query={"language": language}, verbose=verbose
    )
    result = response_to_df(data)

    if verbose and len(result) > 0:
        _msg.success(f"{len(result)} records found")

    return result
