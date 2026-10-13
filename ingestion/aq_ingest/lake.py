from pathlib import Path

import pandas as pd


def write_partition(
    df: pd.DataFrame,
    lake_root: str | Path,
    dataset: str,
    city: str,
    start: str,
    end: str,
) -> Path:
    """Ecrit un fichier Parquet dans raw/<dataset>/city=<ville>/<debut>_<fin>.parquet.

    Reecrire la meme periode remplace le fichier : l'operation est idempotente.
    """
    out_dir = Path(lake_root) / "raw" / dataset / f"city={city}"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{start}_{end}.parquet"
    df.to_parquet(path, index=False)
    return path
