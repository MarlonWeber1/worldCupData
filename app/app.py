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
page = st.sidebar.radio("Navigation", ["Main", "Shot Map"])

if page == "Main":
    st.title("Tournament Data")

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

    st.divider()

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Top Scorers")
        top_scorers = (
            df_shots[df_shots["shot_type"] == "goal"]
            .groupby("player_id")
            .size()
            .rename("Goals")
            .reset_index()
            .merge(df_player, on="player_id")
            .merge(
                df_player_match[["player_id", "team_key"]].drop_duplicates("player_id"),
                on="player_id",
                how="left",
            )
            .merge(df_teams[["team_key", "team_code"]], on="team_key", how="left")
            .sort_values("Goals", ascending=False)
            .head(10)
        )
        st.dataframe(
            top_scorers[["player_name", "team_code", "player_position", "Goals"]].rename(
                columns={"player_name": "Player", "team_code": "Team", "player_position": "Position"}
            ),
            hide_index=True,
            width="stretch",
        )

    with col_right:
        st.subheader("Highest xG Tournament")
        top_xg = (
            non_own.groupby("player_id")["xg"]
            .sum()
            .rename("xG")
            .reset_index()
            .merge(df_player, on="player_id")
            .merge(
                df_player_match[["player_id", "team_key"]].drop_duplicates("player_id"),
                on="player_id",
                how="left",
            )
            .merge(df_teams[["team_key", "team_code"]], on="team_key", how="left")
            .sort_values("xG", ascending=False)
            .head(10)
        )
        top_xg["xG"] = top_xg["xG"].round(2)
        st.dataframe(
            top_xg[["player_name", "team_code", "player_position", "xG"]].rename(
                columns={"player_name": "Player", "team_code": "Team", "player_position": "Position"}
            ),
            hide_index=True,
            width="stretch"
        )

    st.divider()

    st.subheader("Player's performance")
    player_performance = (
        non_own.groupby("player_id")
        .agg(
            shots=("xg", "count"),  # total shots
            xg_total=("xg", "sum"),  # total xG
            xgot_total=("xgot", "sum"),  # total xGOT
            goals=("shot_type", lambda x: (x == "goal").sum()),  # goals
        )
        .reset_index()
    )

    player_performance["xg_per_shot"] = (
        player_performance["xg_total"] / player_performance["shots"]
    )
    player_performance["plus_minus"] = (
        player_performance["goals"] - player_performance["xg_total"]
    )

    matches_per_player = (
        df_player_match.groupby("player_id").agg(
            total_matches=("match_id", "nunique"),
            team_key=("team_key", "first"),
        ).reset_index()
    )

    player_performance = player_performance.merge(
        matches_per_player, on="player_id", how="left"
    )
    player_performance = player_performance.merge(df_player, on="player_id")
    player_performance = player_performance.merge(
        df_teams[["team_key", "team_code"]], on="team_key", how="left"
    )
    
    player_performance = player_performance.sort_values(["goals"], ascending=False)

    st.dataframe(
        player_performance[
            [
                "player_name",
                "team_code",
                "total_matches",
                "shots",
                "goals",
                "xg_total",
                "xg_per_shot",
                "xgot_total",
                "plus_minus",
            ]
        ].rename(
            columns={
                "player_name": "Player",
                "team_code": "Team",
                "total_matches": "Matches",
                "shots": "Shots",
                "goals": "Goals",
                "xg_total": "xG",
                "xg_per_shot": "xG/Shot",
                "xgot_total": "xGOT",
                "plus_minus": "+/-",
            }
        ),
        hide_index=True,
        width="stretch",
    )


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
        st.info("Pick your player")
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
            m5.metric("Average Distance", f"{stats['avg_distance_meters']:.1f} m")

            fig = plot_shot_map(player_row, shots, stats)
            st.pyplot(fig)
