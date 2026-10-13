import argparse
import os
import time

from . import lake, open_meteo
from .config import load_cities

DATASETS = {
    "air_quality": (open_meteo.AIR_QUALITY_URL, open_meteo.AIR_QUALITY_VARS),
    "weather": (open_meteo.WEATHER_URL, open_meteo.WEATHER_VARS),
}


def run_open_meteo(dataset: str, start: str, end: str, lake_root: str, pause: float = 1.0) -> None:
    url, variables = DATASETS[dataset]
    for city, (lat, lon) in load_cities().items():
        payload = open_meteo.fetch_hourly(url, variables, lat, lon, start, end)
        df = open_meteo.to_dataframe(payload, city, lat, lon)
        path = lake.write_partition(df, lake_root, dataset, city, start, end)
        print(f"{city}: {len(df)} lignes -> {path}")
        time.sleep(pause)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="aq_ingest")
    parser.add_argument("dataset", choices=sorted(DATASETS))
    parser.add_argument("--start", required=True, help="Date de debut, format AAAA-MM-JJ")
    parser.add_argument("--end", required=True, help="Date de fin, format AAAA-MM-JJ")
    parser.add_argument("--lake-root", default=os.environ.get("LAKE_ROOT", "/lake"))
    args = parser.parse_args(argv)
    run_open_meteo(args.dataset, args.start, args.end, args.lake_root)
