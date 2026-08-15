import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import streamlit as st

from data_loader import load_refined_tables
from shot_map import get_player_shots, calculate_stats, plot_shot_map

st.set_page_config(
    page_title="World Cup Data Engineering",
    layout="wide",
)

DARK_BG = "#0C0D0E"
ACCENT = "#E4053A"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {DARK_BG}; }}
    [data-testid="stMetricValue"] {{ color: {ACCENT}; }}
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    tables = load_refined_tables()
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()

df_shots = tables["fact_shots"]
df_player = tables["dim_player"]
df_player_match = tables["fact_player_match"]
df_match = tables["dim_match"]
df_teams = tables["dim_national_teams"]

st.sidebar.title("⚽ World Cup Data")
page = st.sidebar.radio("Nave bar", ["Main", "Shot Map"])


if page == "Main":
    st.title("Tourmanent Data")

    non_own = df_shots[df_shots["result"] != "own"]
    total_matches = df_match["match_id"].nunique()
    total_goals = int((df_shots["shot_type"] == "goal").sum())
    total_shots = len(non_own)
    total_xg = non_own["xg"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Matches", total_matches)
    c2.metric("Goals", total_goals)
    c3.metric("Shots", total_shots)
    c4.metric("xG", f"{total_xg:.1f}")


else:
    st.title("Shot Map by Player")

    shooters = (
        df_shots[df_shots["result"] != "own"]["player_id"]
        .drop_duplicates()
        .to_frame()
        .merge(df_player, on="player_id")
        .sort_values("player_name")
    )

    with st.sidebar:
        st.markdown("---")
        selected_name = st.selectbox(
            "Player",
            options=shooters["player_name"].tolist(),
            index=None,
            placeholder="Choose a player...",
        )
        include_own_goals = st.checkbox("Include own goals", value=False)

    if selected_name is None:
        st.info(
            "Pick your player"
        )
    else:
        player_row, shots = get_player_shots(
            df_shots, df_player, selected_name, include_own_goals=include_own_goals
        )

        if shots is None:
            st.warning(
                f"{player_row['player_name']} has no recorded kicks in this tournament"
            )
        else:
            stats = calculate_stats(shots)

            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Shots", stats["total_shots"])
            m2.metric("Goals", stats["total_goals"])
            m3.metric("xG", f"{stats['total_xg']:.2f}")
            m4.metric("xG per shot", f"{stats['xg_per_shot']:.2f}")
            m5.metric("Avarege distance", f"{stats['avg_distance_meters']:.1f} m")

            fig = plot_shot_map(player_row, shots, stats)
            st.pyplot(fig)

