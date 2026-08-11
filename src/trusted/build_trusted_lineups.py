import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql.types import IntegerType, DoubleType

spark = SparkSession.builder.master("local[*]").appName("WorldCupTrusted").getOrCreate()

df = spark.read.csv("../../data/raw/raw_lineups.csv", header=True, inferSchema=False)

df.printSchema()

df_lineups = df.select(
    col("`player.id`").cast(IntegerType()).alias("player_id"),
    col("match_id").cast(IntegerType()).alias("match_id"),
    col("`player.name`").alias("player_name"),
    col("`player.position`").alias("player_position"),
    col("`statistics.minutesPlayed`")
    .cast(DoubleType())
    .cast(IntegerType())
    .alias("minutes_played"),
    col("`statistics.goals`").cast(DoubleType()).cast(IntegerType()).alias("goals"),
    col("`statistics.assists`").cast(DoubleType()).cast(IntegerType()).alias("assists"),
)

df_lineups.printSchema()

# drop rows that idk the player_id or match_id
df_lineups = df_lineups.dropna(subset=["player_id", "match_id"])

# fill missing values
df_lineups = df_lineups.fillna(
    {
        "player_position": "unknown",
        "goals": 0,
        "assists": 0,
    }
)

# drop rows from player that did not play any minute 
df_lineups = df_lineups.dropna(subset=["minutes_played"])

# verify if exists any rule to apply in the text of this columns
df_lineups.select("player_position").distinct().show()

# map abbreviated positions to full names
df_lineups = df_lineups.withColumn(
    "player_position",
    when(col("player_position") == "G", "Goalkeeper")
    .when(col("player_position") == "D", "Defender")
    .when(col("player_position") == "M", "Midfielder")
    .when(col("player_position") == "F", "Forward")
    .otherwise(col("player_position")),
)

df_lineups.select("player_position").distinct().show()

# data validation
invalid_minutes = df_lineups.filter(
    (col("minutes_played") < 0) | (col("minutes_played") > 130)
).count()
invalid_goals = df_lineups.filter(col("goals") < 0).count()
invalid_assists = df_lineups.filter(col("assists") < 0).count()

print(f"Invalid minutes played: {invalid_minutes}, Invalid goals: {invalid_goals}, Invalid assists: {invalid_assists}")

# verify if there are any duplicate (one player that played in the same match more than once
duplicate_lineups = (
    df_lineups
    .groupBy("player_id", "match_id")
    .count()
    .filter(col("count") > 1)
)

duplicate_lineups.show()


# write the trusted lineups data to parquet
df_lineups.write.mode("overwrite").parquet("../../data/trusted/lineups")

spark.stop()
