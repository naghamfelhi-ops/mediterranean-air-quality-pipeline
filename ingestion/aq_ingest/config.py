from pathlib import Path

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config" / "cities.yml"


def load_cities(path: Path = DEFAULT_CONFIG) -> dict[str, tuple[float, float]]:
    """Retourne {ville: (latitude, longitude)} depuis le fichier de configuration."""
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return {name: (c["latitude"], c["longitude"]) for name, c in raw["cities"].items()}
