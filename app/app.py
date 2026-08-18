import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from data_loader import load_refined_tables
from shot_map import get_player_shots, calculate_stats, plot_shot_map

st.set_page_config(
    page_title="World Cup Data Engineering",
    layout="wide",
)

DARK_BG = "#0C0D0E"
ACCENT = "#38BDF8"

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

    player_performance["xg_total"] = player_performance["xg_total"].round(2)
    player_performance["xg_per_shot"] = player_performance["xg_per_shot"].round(2)
    player_performance["xgot_total"] = player_performance["xgot_total"].round(2)
    player_performance["plus_minus"] = player_performance["plus_minus"].round(2)
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

    st.divider()
    col_left2, col_right2 = st.columns([1, 1])

    with col_left2:
        st.subheader("Team Efficiency — Goals vs xG")
        national_teams = (
            non_own.groupby("team_key")
            .agg(
                goals=("shot_type", lambda x: (x == "goal").sum()),
                xG=("xg", "sum"),
            )
            .reset_index()
            .merge(
                df_teams[["team_key", "team_name", "continent"]],
                on="team_key",
                how="left",
            )
        )
        national_teams["xG"] = national_teams["xG"].round(2)
        national_teams["+/-"] = (national_teams["goals"] - national_teams["xG"]).round(2)
        national_teams = national_teams.sort_values("+/-", ascending=False).head(10)
        st.dataframe(
            national_teams[["team_name", "continent", "goals", "xG", "+/-"]].rename(
                columns={"team_name": "Team", "continent": "Continent", "goals": "Goals"}
            ),
            hide_index=True,
            width="stretch",
        )

    with col_right2:
        st.subheader("Shot Conversion Rate by Continent & Situation")

        continent_info = non_own.merge(
            df_teams[["team_key", "continent"]], on="team_key", how="left"
        )

        continent_goals_situation = (
            continent_info[continent_info["shot_type"] == "goal"]
            .groupby(["continent", "situation"])
            .size()
            .rename("goals")
            .reset_index()
        )

        continent_total_shots = (
            continent_info.groupby(["continent", "situation"])
            .agg(total_shots=("xg", "count"))
            .reset_index()
        )

        continent_goals_situation = continent_goals_situation.merge(
            continent_total_shots, on=["continent", "situation"], how="left"
        )

        continent_goals_situation["conversion_rate"] = (
            continent_goals_situation["goals"]
            / continent_goals_situation["total_shots"]
        ).round(2)

        pivot = continent_goals_situation.pivot_table(
            index="continent", 
            columns="situation",  
            values="conversion_rate",  
            fill_value = 0
        )
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor("#0C0D0E")
        ax.set_facecolor("#0C0D0E")
        pivot.plot(kind="bar", ax=ax, width=0.7)
        ax.set_xlabel("")
        ax.set_xticklabels(pivot.index, rotation=30, ha="right", color="white", fontsize = 15)
        ax.tick_params(colors="white")
        legend = ax.legend(facecolor="#0C0D0E", labelcolor="white", edgecolor="gray", title="Situation")
        legend.get_title().set_color("white")
        ax.grid(True, alpha=0.2, axis="y")
        st.pyplot(fig)
        plt.close(fig)

    st.divider()
    st.subheader("Goals, xG & xGOT — Top 16 National Teams")

    national_teams_performance = (
        non_own.groupby("team_key")
        .agg(
            national_teams_goals=("shot_type", lambda x: (x == "goal").sum()),
            national_teams_xg=("xg", "sum"),
            national_teams_xgot=("xgot", "sum"),
        )
        .reset_index()
        .sort_values(["national_teams_goals"], ascending=False)
        .head(16)
    )

    national_teams_performance = national_teams_performance.merge(
        df_teams[["team_key", "team_name"]], on="team_key", how="left"
    )

    national_teams_performance["national_teams_xg"] = national_teams_performance["national_teams_xg"].round(2)
    national_teams_performance["national_teams_xgot"] = national_teams_performance["national_teams_xgot"].round(2)

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor("#0C0D0E")
    ax.set_facecolor("#0C0D0E")

    x = np.arange(len(national_teams_performance))
    bar_width = 0.20

    ax.bar(
        x - bar_width,
        national_teams_performance["national_teams_goals"],
        width=bar_width,
        label="Goals",
        color="#003f5c"
    )
    ax.bar(
        x,
        national_teams_performance["national_teams_xg"],
        width=bar_width,
        label="xG",
        color="#008c54"
    )
    ax.bar(
        x + bar_width,
        national_teams_performance["national_teams_xgot"],
        width=bar_width,
        label="xGOT",
        color="#ffa600"
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        national_teams_performance["team_name"], rotation=45, ha="right", color="white"
    )
    ax.set_ylabel("Total", color="white")
    ax.yaxis.label.set_color("white")
    ax.tick_params(colors="white")
    ax.legend(facecolor="#0C0D0E", labelcolor="white", edgecolor="gray")
    ax.grid(True, alpha=0.2)
    # render
    st.pyplot(fig)
    plt.close(fig)

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
