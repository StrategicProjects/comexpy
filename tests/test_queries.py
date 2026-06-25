import json

import pytest
import responses

import comexpy
from comexpy._client import BASE_URL, set_options


@pytest.fixture(autouse=True)
def _quiet_and_fast():
    comexpy.set_verbose(False)
    set_options(retry_time=0)
    yield
    comexpy.set_verbose(True)


@responses.activate
def test_comex_export_builds_correct_body():
    responses.add(
        responses.POST,
        f"{BASE_URL}/general",
        json={"data": {"list": [{"country": "China", "metricFOB": 100}], "count": 1}},
        status=200,
    )
    df = comexpy.comex_export(
        start_period="2024-01",
        end_period="2024-12",
        details=["country", "hs4"],
        filters={"country": 160},
        metric_cif=True,
    )
    assert df.shape == (1, 2)

    body = json.loads(responses.calls[0].request.body)
    assert body["flow"] == "export"
    assert body["period"] == {"from": "2024-01", "to": "2024-12"}
    assert body["details"] == ["country", "heading"]
    assert body["filters"] == [{"filter": "country", "values": [160]}]
    assert "metricCIF" in body["metrics"]
    # language passed as query param
    assert "language=en" in (responses.calls[0].request.url or "")


@responses.activate
def test_comex_import_flow():
    responses.add(
        responses.POST,
        f"{BASE_URL}/general",
        json={"data": {"list": [], "count": 0}},
        status=200,
    )
    comexpy.comex_import(start_period="2024-01", end_period="2024-01", details="country")
    body = json.loads(responses.calls[0].request.body)
    assert body["flow"] == "import"


@responses.activate
def test_comex_query_city_only_fob_kg():
    responses.add(
        responses.POST,
        f"{BASE_URL}/cities",
        json={"data": [{"city": "Recife", "metricFOB": 5}]},
        status=200,
    )
    df = comexpy.comex_query_city(
        flow="export",
        start_period="2023-01",
        end_period="2023-12",
        details=["city", "state"],
        filters={"state": 26},
    )
    assert df.shape == (1, 2)
    body = json.loads(responses.calls[0].request.body)
    assert body["metrics"] == ["metricFOB", "metricKG"]
    assert body["details"] == ["city", "state"]


@responses.activate
def test_comex_historical_endpoint_and_warning():
    responses.add(
        responses.POST,
        f"{BASE_URL}/historical-data/",
        json={"data": [{"country": "Argentina"}]},
        status=200,
    )
    df = comexpy.comex_historical(
        flow="export", start_period="1995-01", end_period="1996-12", details="country"
    )
    assert df.shape == (1, 1)
    assert responses.calls[0].request.url.rstrip("?").endswith("/historical-data/") or \
        "/historical-data/" in responses.calls[0].request.url


def test_comex_export_invalid_period():
    with pytest.raises(ValueError):
        comexpy.comex_export(start_period="2024-13-01", end_period="2024-12")


@responses.activate
def test_comex_countries_search_passthrough():
    responses.add(
        responses.GET,
        f"{BASE_URL}/tables/countries",
        json={"data": {"list": [{"id": 160, "text": "China"}], "count": 1}},
        status=200,
    )
    df = comexpy.comex_countries(search="china")
    assert df.iloc[0]["text"] == "China"
    assert "search=china" in (responses.calls[0].request.url or "")


@responses.activate
def test_comex_country_detail_extracts_single():
    responses.add(
        responses.GET,
        f"{BASE_URL}/tables/countries/105",
        json={"data": {"id": 105, "text": "Brasil"}},
        status=200,
    )
    out = comexpy.comex_country_detail(105)
    assert out == {"id": 105, "text": "Brasil"}


@responses.activate
def test_comex_details_type_routing():
    responses.add(
        responses.GET,
        f"{BASE_URL}/cities/details",
        json={"data": {"list": [{"id": "country"}], "count": 1}},
        status=200,
    )
    df = comexpy.comex_details("city")
    assert df.shape == (1, 1)


def test_comex_details_invalid_type():
    with pytest.raises(ValueError):
        comexpy.comex_details("nope")


@responses.activate
def test_comex_isic_uses_general_filter_endpoint():
    responses.add(
        responses.GET,
        f"{BASE_URL}/general/filters/ISICSection",
        json={"data": [[{"id": "A", "text": "Agriculture"}]]},
        status=200,
    )
    df = comexpy.comex_isic("section")
    assert df.iloc[0]["text"] == "Agriculture"


def test_comex_isic_invalid_level():
    with pytest.raises(ValueError):
        comexpy.comex_isic("galaxy")
