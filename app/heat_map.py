import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
import pandas as pd


def plot_heat_map(
    df_shots: pd.DataFrame,
    background_color: str = "#0C0D0E",
    cmap: str = "magma",
    title: str = "Shot HeatMap — World Cup 2026",
) -> plt.Figure:
    
    df_heat_map = df_shots[df_shots["result"] != "own"].copy()
    df_heat_map["x"] = 100 - df_heat_map["coord_x"]
    df_heat_map["y"] = df_heat_map["coord_y"]

    pitch = VerticalPitch(
        pitch_type="opta",
        half=True,
        pitch_color=background_color,
        line_color="white",
        linewidth=0.75,
    )

    fig, ax = pitch.draw(figsize=(6, 8))
    fig.patch.set_facecolor(background_color)

    pitch.kdeplot(
        df_heat_map["x"],
        df_heat_map["y"],
        ax=ax,
        fill=True,
        levels=10,
        alpha=0.65,
        cmap=cmap,
    )

    fig.text(
        0.5,
        0.82,
        title,
        color="white",
        fontsize=16,
        fontweight="bold",
        ha="center",
    )

    return fig
