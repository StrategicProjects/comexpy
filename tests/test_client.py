import pytest
import responses

from comexpy._client import BASE_URL, ComexError, comex_get, comex_post, get_options, set_options


@pytest.fixture(autouse=True)
def _reset_options():
    saved = get_options()
    # Avoid real sleeps between retries during tests.
    set_options(retry_time=0)
    yield
    set_options(**{
        "timeout_get": saved["timeout_get"],
        "timeout_post": saved["timeout_post"],
        "max_tries": saved["max_tries"],
        "retry_time": saved["retry_time"],
        "ssl_verify": saved["ssl_verify"],
    })


@responses.activate
def test_comex_get_ok():
    responses.add(
        responses.GET,
        f"{BASE_URL}/tables/uf",
        json={"data": [{"id": 26, "text": "PE"}]},
        status=200,
    )
    out = comex_get("/tables/uf", verbose=False)
    assert out == {"data": [{"id": 26, "text": "PE"}]}


@responses.activate
def test_comex_get_drops_none_query():
    responses.add(
        responses.GET,
        f"{BASE_URL}/tables/countries",
        json={"data": {"list": []}},
        status=200,
    )
    comex_get("/tables/countries", query={"search": None}, verbose=False)
    # None-valued params must not be sent.
    assert "search" not in (responses.calls[0].request.url or "")


@responses.activate
def test_comex_post_ok():
    responses.add(
        responses.POST,
        f"{BASE_URL}/general",
        json={"data": {"list": [{"x": 1}], "count": 1}},
        status=200,
    )
    out = comex_post("/general", {"flow": "export"}, query={"language": "en"}, verbose=False)
    assert out["data"]["count"] == 1


@responses.activate
def test_http_error_raises_comexerror_with_message():
    responses.add(
        responses.POST,
        f"{BASE_URL}/general",
        json={"message": "Invalid detail item (foo)"},
        status=400,
    )
    with pytest.raises(ComexError) as exc:
        comex_post("/general", {}, verbose=False)
    assert "Invalid detail item" in str(exc.value)
    assert "400" in str(exc.value)


@responses.activate
def test_retry_on_429_then_success():
    responses.add(responses.GET, f"{BASE_URL}/tables/uf", status=429, json={})
    responses.add(
        responses.GET,
        f"{BASE_URL}/tables/uf",
        json={"data": [{"id": 26}]},
        status=200,
    )
    out = comex_get("/tables/uf", verbose=False)
    assert out == {"data": [{"id": 26}]}
    assert len(responses.calls) == 2


@responses.activate
def test_retry_exhausted_returns_last_error():
    set_options(max_tries=2)
    responses.add(responses.GET, f"{BASE_URL}/tables/uf", status=429, json={})
    responses.add(responses.GET, f"{BASE_URL}/tables/uf", status=429, json={})
    with pytest.raises(ComexError):
        comex_get("/tables/uf", verbose=False)
    assert len(responses.calls) == 2


def test_set_options_roundtrip():
    set_options(timeout_get=99, max_tries=7)
    cfg = get_options()
    assert cfg["timeout_get"] == 99
    assert cfg["max_tries"] == 7
