from __future__ import annotations

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from mplsoccer import VerticalPitch

BACKGROUND_COLOR = "#0C0D0E"
ACCENT_COLOR = "#38BDF8"

def get_font():
    try:
        return font_manager.FontProperties(family="DejaVu Sans", weight="bold")
    except Exception:
        return None

FONT = get_font()

def get_player_shots(
    df_shots: pd.DataFrame,
    df_player: pd.DataFrame,
    player_name: str,
    include_own_goals: bool = False,
):
    match = df_player[df_player["player_name"].str.lower() == player_name.strip().lower()]

    if match.empty:
        return None, None

    player_row = match.iloc[0]
    shots = df_shots[df_shots["player_id"] == player_row["player_id"]].copy()

    if not include_own_goals:
        shots = shots[shots["result"] != "own"]

    if shots.empty:
        return player_row, None

    # own goals doesn't count 
    shots["xg"] = shots["xg"].fillna(0.0)
    shots["pitch_x"] = 100 - shots["coord_x"]
    shots["pitch_y"] = shots["coord_y"]
    shots["is_goal"] = shots["shot_type"] == "goal"

    return player_row, shots


def calculate_stats(shots: pd.DataFrame) -> dict:
    total_shots = len(shots)
    total_goals = int(shots["is_goal"].sum())
    total_xg = shots["xg"].sum()
    xg_per_shot = total_xg / total_shots if total_shots else 0.0
    avg_distance_meters = shots["coord_x"].mean() * 1.2 * 0.9144

    return {
        "total_shots": total_shots,
        "total_goals": total_goals,
        "total_xg": total_xg,
        "xg_per_shot": xg_per_shot,
        "avg_distance_meters": avg_distance_meters,
    }


def plot_shot_map(
    player_row: pd.Series,
    shots: pd.DataFrame,
    stats: dict,
    subtitle: str = "Shots World Cup",
):
    pitch = VerticalPitch(
        pitch_type="opta", half=True, pitch_color=BACKGROUND_COLOR,
        pad_bottom=.5, line_color="white", linewidth=.75, axis=True, label=True,
    )

    fig = plt.figure(figsize=(8, 11))
    fig.patch.set_facecolor(BACKGROUND_COLOR)

    # names and subtitles
    ax1 = fig.add_axes([0, 0.7, 1, .2])
    ax1.set_facecolor(BACKGROUND_COLOR)
    ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)

    ax1.text(0.5, .85, player_row["player_name"], fontsize=20,
              fontproperties=FONT, fontweight="bold", color="white", ha="center")
    ax1.text(0.5, .7, subtitle, fontsize=13, fontweight="bold",
              fontproperties=FONT, color="white", ha="center")

    ax1.text(0.25, 0.5, "Low Quality Chance", fontsize=11,
              fontproperties=FONT, color="white", ha="center")
    for i, x in enumerate([0.37, 0.42, 0.48, 0.54, 0.60]):
        ax1.scatter(x=x, y=0.53, s=100 * (i + 1), color=BACKGROUND_COLOR,
                    edgecolor="white", linewidth=.8)
    ax1.text(0.75, 0.5, "High Quality Chance", fontsize=11,
              fontproperties=FONT, color="white", ha="center")

    ax1.text(0.45, 0.27, "Goal", fontsize=10, fontproperties=FONT, color="white", ha="right")
    ax1.scatter(x=0.47, y=0.3, s=100, color=ACCENT_COLOR, edgecolor="white", linewidth=.8, alpha=.85)
    ax1.scatter(x=0.53, y=0.3, s=100, color=BACKGROUND_COLOR, edgecolor="white", linewidth=.8)
    ax1.text(0.55, 0.27, "No Goal", fontsize=10, fontproperties=FONT, color="white", ha="left")
    ax1.set_axis_off()

    # field
    ax2 = fig.add_axes([.05, 0.22, .9, .5])
    ax2.set_facecolor(BACKGROUND_COLOR)
    pitch.draw(ax=ax2)

    avg_dist_pitch_x = 100 - (stats["avg_distance_meters"] / (1.2 * 0.9144))
    ax2.scatter(x=90, y=avg_dist_pitch_x, s=100, color="white", linewidth=.8)
    ax2.plot([90, 90], [100, avg_dist_pitch_x], color="white", linewidth=2)
    ax2.text(90, avg_dist_pitch_x - 4,
              f"Average Distance\n{stats['avg_distance_meters']:.1f} m",
              fontsize=10, fontproperties=FONT, color="white", ha="center")

    for shot in shots.to_dict(orient="records"):
        pitch.scatter(
            shot["pitch_x"], shot["pitch_y"],
            s=max(300 * shot["xg"], 20),
            color=ACCENT_COLOR if shot["is_goal"] else BACKGROUND_COLOR,
            ax=ax2, alpha=.75, linewidth=.8, edgecolor="white",
        )
    ax2.set_axis_off()

    return fig
