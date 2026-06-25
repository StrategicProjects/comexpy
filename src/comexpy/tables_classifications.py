"""Economic classification auxiliary tables (CGCE, SITC/CUCI, ISIC)."""
from __future__ import annotations

from typing import Optional

import pandas as pd

from ._client import comex_get
from ._format import response_to_df
from .tables import comex_filter_values

# ---- CGCE - Classification by Broad Economic Categories -----------------


def comex_cgce(
    language: str = "en",
    search: Optional[str] = None,
    add: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """CGCE (Classification by Broad Economic Categories) table.

    CGCE groups products by use or economic purpose (e.g. capital goods,
    intermediate goods, consumer goods). Served by ``/tables/classifications``.

    Parameters
    ----------
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    search : str, optional
        Search term to filter results.
    add : str, optional
        Related table to include (e.g. ``"ncm"``).
    page, per_page : int, optional
        Pagination controls.
    verbose : bool
        Show progress messages (default ``False``).
    """
    data = comex_get(
        "/tables/classifications",
        query={
            "language": language,
            "search": search,
            "add": add,
            "page": page,
            "perPage": per_page,
        },
        verbose=verbose,
    )
    return response_to_df(data)


# ---- SITC / CUCI - Standard International Trade Classification ----------


def comex_sitc(
    language: str = "en",
    search: Optional[str] = None,
    add: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """SITC/CUCI (Standard International Trade Classification) table.

    CUCI is the Portuguese name for SITC. Served by the
    ``/tables/product-categories`` endpoint.

    Parameters
    ----------
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    search : str, optional
        Search term to filter results (e.g. ``"carne"``).
    add : str, optional
        Related table to include (e.g. ``"ncm"``).
    page, per_page : int, optional
        Pagination controls.
    verbose : bool
        Show progress messages (default ``False``).
    """
    data = comex_get(
        "/tables/product-categories",
        query={
            "language": language,
            "search": search,
            "add": add,
            "page": page,
            "perPage": per_page,
        },
        verbose=verbose,
    )
    return response_to_df(data)


# ---- ISIC - International Standard Industrial Classification ------------

_ISIC_FILTERS = {
    "section": "ISICSection",
    "division": "ISICDivision",
    "group": "ISICGroup",
    "class": "ISICClass",
}


def comex_isic(
    level: str = "section", language: str = "en", verbose: bool = False
) -> pd.DataFrame:
    """ISIC (International Standard Industrial Classification) values.

    Retrieves ISIC values at a chosen hierarchical level via the
    ``/general/filters/{filter}`` endpoint, which is the only place the
    ComexStat API exposes ISIC codes (there is no ``/tables/isic`` endpoint).

    Parameters
    ----------
    level : str
        Hierarchical level: ``"section"``, ``"division"``, ``"group"`` or
        ``"class"`` (default ``"section"``).
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    verbose : bool
        Show progress messages (default ``False``).
    """
    try:
        filter_name = _ISIC_FILTERS[level]
    except KeyError:
        raise ValueError(
            f"Invalid level: {level}. "
            "Use 'section', 'division', 'group', or 'class'."
        )
    return comex_filter_values(
        filter_name, type="general", language=language, verbose=verbose
    )
