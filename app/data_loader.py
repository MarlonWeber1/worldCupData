from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.dataset as ds
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "refined"


def _load_table(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            "Didn't find the path"
        )
    return ds.dataset(path, format="parquet").to_table().to_pandas()


@st.cache_data(show_spinner="Loading refined data...")
def load_refined_tables() -> dict[str, pd.DataFrame]:
    return {
        "fact_shots": _load_table("fact_shots"),
        "dim_player": _load_table("dim_player"),
        "fact_player_match": _load_table("fact_player_match"),
        "dim_match": _load_table("dim_match"),
        "dim_national_teams": _load_table("dim_national_teams"),
    }
