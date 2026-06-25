"""General foreign trade data queries (POST ``/general``)."""
from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence, Union

import pandas as pd

from . import _msg
from ._client import comex_post
from ._format import (
    build_details,
    build_filters,
    build_metrics,
    convert_flow,
    response_to_df,
    validate_period,
)

Details = Union[str, Sequence[str], None]
Filters = Optional[Mapping[str, Any]]


def comex_query(
    flow: str = "export",
    start_period: str = None,
    end_period: str = None,
    details: Details = None,
    filters: Filters = None,
    month_detail: bool = True,
    metric_fob: bool = True,
    metric_kg: bool = True,
    metric_statistic: bool = False,
    metric_freight: bool = False,
    metric_insurance: bool = False,
    metric_cif: bool = False,
    language: str = "en",
    verbose: bool = True,
) -> pd.DataFrame:
    """Query general Brazilian foreign trade data (1997-present).

    Supports filtering and grouping by multiple classifications such as NCM,
    Harmonized System, countries, states, etc. Data is available monthly from
    1997 to the most recent complete month.

    Parameters
    ----------
    flow : str
        Trade flow: ``"export"`` or ``"import"``.
    start_period, end_period : str
        Period bounds in ``"YYYY-MM"`` format (e.g. ``"2023-01"``).
    details : str or sequence of str, optional
        Detail/grouping fields. The names below are user-friendly aliases;
        the package translates each to the underlying API name. The API names
        returned by ``comex_details("general")`` are also accepted verbatim.

        * **Geographic:** ``"country"``, ``"bloc"`` (``"economic_block"``),
          ``"state"``, ``"transport_mode"`` (API ``via``),
          ``"customs_unit"`` (API ``urf``)
        * **Products:** ``"ncm"``, ``"hs6"``/``"sh6"`` (API ``subHeading``),
          ``"hs4"``/``"sh4"`` (API ``heading``), ``"hs2"``/``"sh2"``
          (API ``chapter``), ``"section"``
        * **CGCE (BEC):** ``"cgce_n1"``, ``"cgce_n2"``, ``"cgce_n3"``
        * **SITC/CUCI:** ``"sitc_section"``, ``"sitc_division"``,
          ``"sitc_group"``, ``"sitc_subgroup"``, ``"sitc_basic_heading"``
        * **ISIC:** ``"isic_section"``, ``"isic_division"``,
          ``"isic_group"``, ``"isic_class"``
    filters : mapping, optional
        Mapping of filter name to value(s). Names match the detail fields.
        Example: ``{"country": [160, 249], "state": [26, 13]}``.
    month_detail : bool
        If ``True`` (default), break down results by month.
    metric_fob, metric_kg, metric_statistic, metric_freight, \
metric_insurance, metric_cif : bool
        Metrics to include. FOB (US$) and net weight (kg) default to ``True``;
        freight, insurance and CIF apply to imports only.
    language : str
        Response language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    verbose : bool
        Show progress messages (default ``True``).

    Returns
    -------
    pandas.DataFrame
        The query results.

    Examples
    --------
    >>> comex_query(flow="export", start_period="2023-01",
    ...             end_period="2023-12", details="country")  # doctest: +SKIP
    """
    validate_period(start_period, end_period)
    flow_api = convert_flow(flow)

    if verbose:
        label = "exports" if flow_api == "export" else "imports"
        _msg.info(f"Querying {label} from {start_period} to {end_period}")

    body = {
        "flow": flow_api,
        "monthDetail": month_detail,
        "period": {"from": start_period, "to": end_period},
        "filters": build_filters(filters),
        "details": build_details(details),
        "metrics": build_metrics(
            metric_fob=metric_fob,
            metric_kg=metric_kg,
            metric_statistic=metric_statistic,
            metric_freight=metric_freight,
            metric_insurance=metric_insurance,
            metric_cif=metric_cif,
        ),
    }

    data = comex_post("/general", body, query={"language": language}, verbose=verbose)
    result = response_to_df(data)

    if verbose and len(result) > 0:
        _msg.success(f"{len(result)} records found")

    return result


def comex_export(
    start_period: str,
    end_period: str,
    details: Details = None,
    filters: Filters = None,
    month_detail: bool = True,
    metric_fob: bool = True,
    metric_kg: bool = True,
    metric_statistic: bool = False,
    metric_freight: bool = False,
    metric_insurance: bool = False,
    metric_cif: bool = False,
    language: str = "en",
    verbose: bool = True,
) -> pd.DataFrame:
    """Query exports — shortcut for :func:`comex_query` with ``flow="export"``."""
    return comex_query(
        flow="export",
        start_period=start_period,
        end_period=end_period,
        details=details,
        filters=filters,
        month_detail=month_detail,
        metric_fob=metric_fob,
        metric_kg=metric_kg,
        metric_statistic=metric_statistic,
        metric_freight=metric_freight,
        metric_insurance=metric_insurance,
        metric_cif=metric_cif,
        language=language,
        verbose=verbose,
    )


def comex_import(
    start_period: str,
    end_period: str,
    details: Details = None,
    filters: Filters = None,
    month_detail: bool = True,
    metric_fob: bool = True,
    metric_kg: bool = True,
    metric_statistic: bool = False,
    metric_freight: bool = False,
    metric_insurance: bool = False,
    metric_cif: bool = False,
    language: str = "en",
    verbose: bool = True,
) -> pd.DataFrame:
    """Query imports — shortcut for :func:`comex_query` with ``flow="import"``."""
    return comex_query(
        flow="import",
        start_period=start_period,
        end_period=end_period,
        details=details,
        filters=filters,
        month_detail=month_detail,
        metric_fob=metric_fob,
        metric_kg=metric_kg,
        metric_statistic=metric_statistic,
        metric_freight=metric_freight,
        metric_insurance=metric_insurance,
        metric_cif=metric_cif,
        language=language,
        verbose=verbose,
    )
