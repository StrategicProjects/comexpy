"""comexpy — access the Brazilian Foreign Trade Statistics API (ComexStat).

A pandas-friendly Python port of the R package ``comexr``. Query Brazilian
export and import data — general trade statistics (1997-present), city-level
data, and historical records (1989-1996) — plus auxiliary tables for product
codes (NCM, NBM, HS), countries, economic blocs and classifications (CGCE,
SITC, ISIC). The public function names mirror the R API so knowledge
transfers directly between the two.

Every query/table function returns a :class:`pandas.DataFrame`; detail
functions return a ``dict``.

Quick start
-----------
>>> import comexpy
>>> comexpy.comex_export("2024-01", "2024-12", details="country")   # doctest: +SKIP
>>> comexpy.comex_countries(search="china")                          # doctest: +SKIP
>>> comexpy.comex_details("general")                                 # doctest: +SKIP
"""
from __future__ import annotations

from ._client import BASE_URL, ComexError, get_options, set_options
from ._format import DETAILS_MAP
from ._msg import set_verbose
from .historical import comex_historical
from .query import comex_export, comex_import, comex_query
from .query_city import comex_query_city
from .tables import (
    comex_available_years,
    comex_blocs,
    comex_cities,
    comex_city_detail,
    comex_countries,
    comex_country_detail,
    comex_customs_unit_detail,
    comex_customs_units,
    comex_details,
    comex_filter_values,
    comex_filters,
    comex_last_update,
    comex_metrics,
    comex_state_detail,
    comex_states,
    comex_transport_mode_detail,
    comex_transport_modes,
)
from .tables_classifications import comex_cgce, comex_isic, comex_sitc
from .tables_products import (
    comex_hs,
    comex_nbm,
    comex_nbm_detail,
    comex_ncm,
    comex_ncm_detail,
)

__version__ = "0.1.1"

__all__ = [
    # Query functions (POST)
    "comex_query",
    "comex_export",
    "comex_import",
    "comex_query_city",
    "comex_historical",
    # API metadata (GET)
    "comex_last_update",
    "comex_available_years",
    "comex_filters",
    "comex_filter_values",
    "comex_details",
    "comex_metrics",
    # Auxiliary tables - geography
    "comex_countries",
    "comex_country_detail",
    "comex_blocs",
    "comex_states",
    "comex_state_detail",
    "comex_cities",
    "comex_city_detail",
    "comex_transport_modes",
    "comex_transport_mode_detail",
    "comex_customs_units",
    "comex_customs_unit_detail",
    # Auxiliary tables - products
    "comex_ncm",
    "comex_ncm_detail",
    "comex_nbm",
    "comex_nbm_detail",
    "comex_hs",
    # Auxiliary tables - classifications
    "comex_cgce",
    "comex_sitc",
    "comex_isic",
    # Configuration / helpers
    "set_options",
    "get_options",
    "set_verbose",
    "ComexError",
    "DETAILS_MAP",
    "BASE_URL",
    "__version__",
]
