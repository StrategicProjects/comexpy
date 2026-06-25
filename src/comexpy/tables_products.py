"""Product classification auxiliary tables (NCM, NBM, HS)."""
from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from ._client import comex_get
from ._format import extract_single, response_to_df

# ---- NCM - Mercosur Common Nomenclature ---------------------------------


def comex_ncm(
    language: str = "en",
    search: Optional[str] = None,
    add: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """NCM (Mercosur Common Nomenclature) table with descriptions.

    NCM is the 8-digit product classification used by Mercosur countries,
    based on the Harmonized System (HS).

    Parameters
    ----------
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    search : str, optional
        Search term to filter results (e.g. ``"animal"``).
    add : str, optional
        Related table to include: ``"sh"``, ``"cuci"`` or ``"cgce"``.
    page, per_page : int, optional
        Pagination controls (default returns all results).
    verbose : bool
        Show progress messages (default ``False``).
    """
    data = comex_get(
        "/tables/ncm",
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


def comex_ncm_detail(ncm_code: Any, verbose: bool = False) -> Any:
    """Details for a specific NCM code (8 digits, e.g. ``"02042200"``)."""
    data = comex_get(f"/tables/ncm/{ncm_code}", verbose=verbose)
    return extract_single(data)


# ---- NBM - Brazilian Nomenclature of Goods (Historical) -----------------


def comex_nbm(
    language: str = "en",
    search: Optional[str] = None,
    add: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """NBM (Brazilian Nomenclature of Goods) table with descriptions.

    NBM was used in Brazil before NCM adoption and applies only to historical
    data (1989-1996).

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
        "/tables/nbm",
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


def comex_nbm_detail(nbm_code: Any, verbose: bool = False) -> Any:
    """Details for a specific NBM code (e.g. ``"2924101100"``)."""
    data = comex_get(f"/tables/nbm/{nbm_code}", verbose=verbose)
    return extract_single(data)


# ---- HS - Harmonized System --------------------------------------------


def comex_hs(
    language: str = "en",
    add: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    verbose: bool = False,
) -> pd.DataFrame:
    """Harmonized System (HS) classification tables.

    The HS is an international product nomenclature developed by the World
    Customs Organization, organised hierarchically: Section, Chapter (HS2),
    Heading (HS4) and Subheading (HS6). NCM adds two more digits to HS6.

    Parameters
    ----------
    language : str
        Language: ``"pt"``, ``"en"`` or ``"es"`` (default ``"en"``).
    add : str, optional
        Related table to include (e.g. ``"ncm"``).
    page, per_page : int, optional
        Pagination controls.
    verbose : bool
        Show progress messages (default ``False``).
    """
    data = comex_get(
        "/tables/hs",
        query={
            "language": language,
            "add": add,
            "page": page,
            "perPage": per_page,
        },
        verbose=verbose,
    )
    return response_to_df(data)
