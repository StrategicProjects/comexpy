"""API metadata and geographic auxiliary tables (GET)."""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from ._client import comex_get
from ._format import extract_single, response_to_df

_DATE_ENDPOINTS = {
    "general": "/general",
    "city": "/cities",
    "historical": "/historical-data",
}


def _base_for(type: str) -> str:
    try:
        return _DATE_ENDPOINTS[type]
    except KeyError:
        raise ValueError(
            f"Invalid type: {type}. Use 'general', 'city', or 'historical'."
        )


# ---- Metadata -----------------------------------------------------------


def comex_last_update(type: str = "general", verbose: bool = False) -> Any:
    """Date of the last data update in the API.

    Parameters
    ----------
    type : str
        Data type: ``"general"``, ``"city"`` or ``"historical"``.
    verbose : bool
        Show progress messages (default ``False``).

    Returns
    -------
    dict
        Last-update information.
    """
    endpoint = _base_for(type) + "/dates/updated"
    return extract_single(comex_get(endpoint, verbose=verbose))


def comex_available_years(type: str = "general", verbose: bool = False) -> Any:
    """First and last years available for queries.

    Parameters
    ----------
    type : str
        Data type: ``"general"``, ``"city"`` or ``"historical"``.
    verbose : bool
        Show progress messages (default ``False``).

    Returns
    -------
    dict
        Mapping with ``min`` and ``max`` year values.
    """
    endpoint = _base_for(type) + "/dates/years"
    return extract_single(comex_get(endpoint, verbose=verbose))


def comex_filters(
    type: str = "general", language: str = "en", verbose: bool = False
) -> pd.DataFrame:
    """List of filter types available for API queries."""
    endpoint = _base_for(type) + "/filters"
    data = comex_get(endpoint, query={"language": language}, verbose=verbose)
    return response_to_df(data)


def comex_filter_values(
    filter: str,
    type: str = "general",
    language: str = "en",
    verbose: bool = False,
) -> pd.DataFrame:
    """Possible values for a given filter.

    The ``filter`` argument is passed verbatim to the API and is
    case-sensitive — use the exact name returned by :func:`comex_filters`
    (e.g. ``"economicBlock"``, ``"BECLevel1"``, ``"SITCSection"``,
    ``"ISICSection"``, ``"subHeading"``, ``"heading"``, ``"chapter"``).

    Parameters
    ----------
    filter : str
        Filter name as returned by :func:`comex_filters`.
    type : str
        Data type: ``"general"``, ``"city"`` or ``"historical"``.
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    verbose : bool
        Show progress messages (default ``False``).
    """
    endpoint = _base_for(type) + "/filters/" + str(filter)
    data = comex_get(endpoint, query={"language": language}, verbose=verbose)
    return response_to_df(data)


def comex_details(
    type: str = "general", language: str = "en", verbose: bool = False
) -> pd.DataFrame:
    """Detail/grouping fields that can be used to group query results."""
    endpoint = _base_for(type) + "/details"
    data = comex_get(endpoint, query={"language": language}, verbose=verbose)
    return response_to_df(data)


def comex_metrics(
    type: str = "general", language: str = "en", verbose: bool = False
) -> pd.DataFrame:
    """Metrics (values) available for API queries."""
    endpoint = _base_for(type) + "/metrics"
    data = comex_get(endpoint, query={"language": language}, verbose=verbose)
    return response_to_df(data)


# ---- Auxiliary tables: Geography ----------------------------------------


def comex_countries(
    search: Optional[str] = None, verbose: bool = False
) -> pd.DataFrame:
    """Countries table with codes and names.

    Parameters
    ----------
    search : str, optional
        Search term to filter results (e.g. ``"bra"``).
    verbose : bool
        Show progress messages (default ``False``).
    """
    data = comex_get(
        "/tables/countries", query={"search": search}, verbose=verbose
    )
    return response_to_df(data)


def comex_country_detail(id: Any, verbose: bool = False) -> Any:
    """Details for a specific country by its code (e.g. ``105`` for Brazil)."""
    data = comex_get(f"/tables/countries/{id}", verbose=verbose)
    return extract_single(data)


def comex_blocs(
    language: str = "en",
    search: Optional[str] = None,
    add: Optional[str] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Economic blocs table (trade agreements between countries/regions).

    Parameters
    ----------
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    search : str, optional
        Search term to filter results.
    add : str, optional
        Related table to include (e.g. ``"country"``).
    verbose : bool
        Show progress messages (default ``False``).
    """
    data = comex_get(
        "/tables/economic-blocks",
        query={"language": language, "search": search, "add": add},
        verbose=verbose,
    )
    return response_to_df(data)


def comex_states(verbose: bool = False) -> pd.DataFrame:
    """Brazilian states (UF) table with codes and names."""
    return response_to_df(comex_get("/tables/uf", verbose=verbose))


def comex_state_detail(uf_id: Any, verbose: bool = False) -> Any:
    """Details for a specific Brazilian state (e.g. ``26`` for Pernambuco)."""
    data = comex_get(f"/tables/uf/{uf_id}", verbose=verbose)
    return extract_single(data)


def comex_cities(verbose: bool = False) -> pd.DataFrame:
    """Brazilian cities table with IBGE codes and names."""
    return response_to_df(comex_get("/tables/cities", verbose=verbose))


def comex_city_detail(city_id: Any, verbose: bool = False) -> Any:
    """Details for a specific Brazilian city (e.g. ``5300050``)."""
    data = comex_get(f"/tables/cities/{city_id}", verbose=verbose)
    return extract_single(data)


def comex_transport_modes(verbose: bool = False) -> pd.DataFrame:
    """Transport modes table with codes and names."""
    return response_to_df(comex_get("/tables/ways", verbose=verbose))


def comex_transport_mode_detail(mode_id: Any, verbose: bool = False) -> Any:
    """Details for a specific transport mode (e.g. ``5`` for maritime)."""
    data = comex_get(f"/tables/ways/{mode_id}", verbose=verbose)
    return extract_single(data)


def comex_customs_units(verbose: bool = False) -> pd.DataFrame:
    """Customs units (URF) table.

    The Federal Revenue Service administrative units (Unidades da Receita
    Federal) responsible for overseeing foreign trade operations.
    """
    return response_to_df(comex_get("/tables/urf", verbose=verbose))


def comex_customs_unit_detail(urf_id: Any, verbose: bool = False) -> Any:
    """Details for a specific customs unit (URF) (e.g. ``8110000``)."""
    data = comex_get(f"/tables/urf/{urf_id}", verbose=verbose)
    return extract_single(data)
