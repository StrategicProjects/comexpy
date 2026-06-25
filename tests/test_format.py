import pandas as pd

from comexpy._format import (
    build_details,
    build_filters,
    build_metrics,
    convert_flow,
    extract_single,
    get_api_name,
    response_to_df,
    validate_period,
)


def test_response_to_df_pattern_list_key():
    # {"data": {"list": [...], "count": N}}
    r = {"data": {"list": [{"a": 1, "b": 2}, {"a": 3, "b": 4}], "count": 2}}
    df = response_to_df(r)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["a", "b"]


def test_response_to_df_pattern_direct_array():
    r = {"data": [{"id": 1, "text": "x"}, {"id": 2, "text": "y"}]}
    df = response_to_df(r)
    assert df.shape == (2, 2)


def test_response_to_df_pattern_double_wrapped():
    r = {"data": [[{"id": "01", "text": "a"}]]}
    df = response_to_df(r)
    assert df.shape == (1, 2)


def test_response_to_df_empty():
    assert response_to_df({"data": None}).empty
    assert response_to_df({"data": []}).empty
    assert response_to_df({"data": {"list": [], "count": 0}}).empty


def test_response_to_df_ragged_rows():
    # Missing keys become NaN columns, not an error.
    r = {"data": [{"a": 1}, {"a": 2, "b": 9}]}
    df = response_to_df(r)
    assert df.shape == (2, 2)
    assert pd.isna(df.loc[0, "b"])


def test_response_to_df_nested_value_flattened():
    r = {"data": [{"a": [1, 2, 3]}]}
    df = response_to_df(r)
    assert df.loc[0, "a"] == "1, 2, 3"


def test_extract_single_named_object():
    assert extract_single({"data": {"id": 105, "country": "Brasil"}}) == {
        "id": 105,
        "country": "Brasil",
    }


def test_extract_single_unnamed_list():
    assert extract_single({"data": [{"id": "02042200"}]}) == {"id": "02042200"}


def test_extract_single_list_key():
    assert extract_single({"data": {"list": [{"x": 1}], "count": 1}}) == {"x": 1}


def test_extract_single_null():
    assert extract_single({"data": None}) is None
    assert extract_single({"data": []}) is None
    assert extract_single(None) is None


def test_get_api_name_alias_and_passthrough():
    assert get_api_name("transport_mode") == "via"
    assert get_api_name("hs4") == "heading"
    assert get_api_name("cgce_n1") == "BECLevel1"
    # API name passes through unchanged
    assert get_api_name("via") == "via"
    assert get_api_name("economicBlock") == "economicBlock"


def test_get_api_name_unknown_warns_and_passes_through(capsys):
    assert get_api_name("totally_unknown") == "totally_unknown"
    err = capsys.readouterr().err
    assert "Unknown detail/filter" in err


def test_build_details():
    assert build_details(["country", "hs4", "cgce_n1"]) == [
        "country",
        "heading",
        "BECLevel1",
    ]
    assert build_details("country") == ["country"]
    assert build_details(None) == []


def test_build_filters():
    out = build_filters({"country": [160, 249], "hs4": "1234"})
    assert out == [
        {"filter": "country", "values": [160, 249]},
        {"filter": "heading", "values": ["1234"]},
    ]
    assert build_filters(None) == []


def test_build_metrics_defaults_and_flags():
    assert build_metrics() == ["metricFOB", "metricKG"]
    assert build_metrics(metric_cif=True) == ["metricFOB", "metricKG", "metricCIF"]


def test_build_metrics_requires_one():
    import pytest

    with pytest.raises(ValueError):
        build_metrics(metric_fob=False, metric_kg=False)


def test_validate_period_ok():
    validate_period("2023-01", "2023-12")


def test_validate_period_bad_format():
    import pytest

    with pytest.raises(ValueError):
        validate_period("2023/01", "2023-12")
    with pytest.raises(ValueError):
        validate_period("2023-01", "bad")


def test_validate_period_order():
    import pytest

    with pytest.raises(ValueError):
        validate_period("2023-12", "2023-01")


def test_convert_flow():
    assert convert_flow("exports") == "export"
    assert convert_flow("EXP") == "export"
    assert convert_flow("imp") == "import"
    assert convert_flow("Import") == "import"


def test_convert_flow_invalid():
    import pytest

    with pytest.raises(ValueError):
        convert_flow("sideways")
