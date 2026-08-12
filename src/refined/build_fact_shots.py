import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

spark = SparkSession.builder.master("local[*]").appName("WorldCupRefined").getOrCreate()

df_shots = spark.read.parquet("../../data/trusted/shots")
df_lineups = spark.read.parquet("../../data/trusted/lineups")
df_match = spark.read.parquet("../../data/trusted/matches")
df_teams = spark.read.parquet("../../data/trusted/national_teams")

# get player side
df_shots_with_lineup = df_shots.join(
    df_lineups.select("player_id", "match_id", "team_side"),
    on=["player_id", "match_id"],
    how="inner",
)

# get home and away teams
df_shots_with_match = df_shots_with_lineup.join(
    df_match.select("match_id", "home_team", "away_team"), on="match_id", how="inner"
)

# determine player national team
df_shots_with_match = df_shots_with_match.withColumn(
    "team_name",
    when(col("team_side") == "home", col("home_team")).when(
        col("team_side") == "away", col("away_team")
    ),
)

# join national team key reference
df_shots_with_team = df_shots_with_match.join(
    df_teams.select("team_key", "team_name"), on="team_name", how="inner"
)

# create the fact_shot
fact_shots = df_shots_with_team.select(
    col("shot_id"),
    col("player_id"),
    col("match_id"),
    col("team_key"),
    col("xg"),
    col("xgot"),
    col("shot_minute"),
    col("added_time"),
    col("coord_x"),
    col("coord_y"),
    col("shot_type"),
    col("situation"),
    col("body_part"),
    col("result")
)

fact_shots.printSchema()

# write the refined fact_shots data to parquet
fact_shots.write.mode("overwrite").parquet("../../data/refined/fact_shots")

spark.stop()
