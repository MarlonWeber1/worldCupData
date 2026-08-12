import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, row_number
from pyspark.sql.window import Window
from pyspark.sql.types import IntegerType

spark = SparkSession.builder.master("local[*]").appName("WorldCupRefined").getOrCreate()

df_match = spark.read.parquet("../../data/trusted/matches")
df_lineups = spark.read.parquet("../../data/trusted/lineups")
df_teams = spark.read.parquet("../../data/trusted/national_teams")

df_match.printSchema()
df_lineups.printSchema()
df_teams.printSchema()

# get the home and away team from the match
df_player_match = df_lineups.join(
    df_match.select("match_id", "home_team", "away_team"), on="match_id", how="inner"
)

# determine player national team
df_player_match = df_player_match.withColumn(
    "team_name",
    when(col("team_side") == "home", col("home_team")).when(
        col("team_side") == "away", col("away_team")
    ),
)

# join national team key reference
df_player_match = df_player_match.join(
    df_teams.select("team_key", "team_name"), on="team_name", how="inner"
)

# create fact
# surrogate key
window_fact = Window.orderBy("player_id", "match_id")

fact_player_match = df_player_match.withColumn(
    "player_match_key", row_number().over(window_fact)
).select(
    col("player_match_key").cast(IntegerType()),
    col("player_id"),
    col("team_key"),
    col("match_id"),
    col("minutes_played"),
    col("goals"),
    col("assists"),
)

# write the refined fact_player_match data to parquet
fact_player_match.write.mode("overwrite").parquet(
    "../../data/refined/fact_player_match"
)

spark.stop()
