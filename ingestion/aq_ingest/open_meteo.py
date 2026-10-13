from datetime import datetime, timezone

import pandas as pd
import requests

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"

AIR_QUALITY_VARS = [
    "pm10",
    "pm2_5",
    "nitrogen_dioxide",
    "ozone",
    "sulphur_dioxide",
    "carbon_monoxide",
]
WEATHER_VARS = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "wind_direction_10m",
]


def fetch_hourly(
    url: str,
    variables: list[str],
    latitude: float,
    longitude: float,
    start: str,
    end: str,
    session=None,
) -> dict:
    """Appelle l'API Open-Meteo et retourne la reponse JSON (heures en UTC)."""
    client = session or requests
    response = client.get(
        url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(variables),
            "start_date": start,
            "end_date": end,
            "timezone": "UTC",
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def to_dataframe(
    payload: dict,
    city: str,
    latitude: float,
    longitude: float,
    ingested_at: datetime | None = None,
) -> pd.DataFrame:
    """Transforme la reponse en tableau et ajoute ville, coordonnees et date d'ingestion."""
    df = pd.DataFrame(payload["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    df["city"] = city
    df["latitude"] = latitude
    df["longitude"] = longitude
    df["ingested_at"] = ingested_at or datetime.now(timezone.utc)
    return df
