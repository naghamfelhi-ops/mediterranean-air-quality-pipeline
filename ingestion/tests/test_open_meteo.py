from datetime import datetime, timezone

import pandas as pd

from aq_ingest import cli, lake, open_meteo
from aq_ingest.config import load_cities

PAYLOAD = {
    "hourly": {
        "time": ["2025-11-05T00:00", "2025-11-05T01:00"],
        "pm10": [10.0, 12.5],
        "pm2_5": [5.0, None],
    }
}


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return PAYLOAD


class FakeSession:
    def __init__(self):
        self.params = None

    def get(self, url, params, timeout):
        self.params = params
        return FakeResponse()


def test_to_dataframe_adds_metadata():
    ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    df = open_meteo.to_dataframe(PAYLOAD, "Tunis", 36.81, 10.18, ingested_at=ts)
    assert len(df) == 2
    assert list(df["city"].unique()) == ["Tunis"]
    assert pd.api.types.is_datetime64_any_dtype(df["time"])
    assert df["ingested_at"].iloc[0] == ts


def test_to_dataframe_keeps_missing_values():
    df = open_meteo.to_dataframe(PAYLOAD, "Tunis", 36.81, 10.18)
    assert df["pm2_5"].isna().sum() == 1


def test_write_partition_layout_and_idempotence(tmp_path):
    df = open_meteo.to_dataframe(PAYLOAD, "Madrid", 40.42, -3.70)
    path = lake.write_partition(df, tmp_path, "air_quality", "Madrid", "2025-11-05", "2025-11-06")
    expected = tmp_path / "raw" / "air_quality" / "city=Madrid" / "2025-11-05_2025-11-06.parquet"
    assert path == expected
    lake.write_partition(df, tmp_path, "air_quality", "Madrid", "2025-11-05", "2025-11-06")
    assert len(list(expected.parent.glob("*.parquet"))) == 1
    assert pd.read_parquet(path).shape[0] == 2


def test_fetch_hourly_sends_expected_params():
    session = FakeSession()
    payload = open_meteo.fetch_hourly(
        open_meteo.AIR_QUALITY_URL,
        ["pm10", "pm2_5"],
        36.81,
        10.18,
        "2025-11-05",
        "2025-11-06",
        session=session,
    )
    assert payload == PAYLOAD
    assert session.params["hourly"] == "pm10,pm2_5"
    assert session.params["timezone"] == "UTC"
    assert session.params["start_date"] == "2025-11-05"


def test_load_cities_contains_the_six_cities():
    cities = load_cities()
    assert sorted(cities) == ["Athens", "Barcelona", "Beirut", "Madrid", "Rome", "Tunis"]
    latitude, longitude = cities["Tunis"]
    assert 36 < latitude < 37 and 10 < longitude < 11


def test_cli_run_writes_one_file_per_city(tmp_path, monkeypatch):
    monkeypatch.setattr(open_meteo, "fetch_hourly", lambda *args, **kwargs: PAYLOAD)
    cli.run_open_meteo("air_quality", "2025-11-05", "2025-11-06", str(tmp_path), pause=0)
    files = list((tmp_path / "raw" / "air_quality").glob("city=*/*.parquet"))
    assert len(files) == 6
