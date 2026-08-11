import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, DoubleType

spark = SparkSession.builder.master("local[*]").appName("WorldCupTrusted").getOrCreate()

df = spark.read.csv("../../data/raw/raw_shotmap.csv", header=True, inferSchema=False)

df.printSchema()

df_shots = df.select(
    col("id").cast(IntegerType()).alias("shot_id"),
    col("match_id").cast(IntegerType()).alias("match_id"),
    col("`player.id`").cast(IntegerType()).alias("player_id"),
    col("`player.name`").alias("player_name"),
    col("xg").cast(DoubleType()).alias("xg"),
    col("xgot").cast(DoubleType()).alias("xgot"),
    col("time").cast(IntegerType()).alias("shot_minute"),
    col("addedTime").cast(DoubleType()).cast(IntegerType()).alias("added_time"),
    col("`playerCoordinates.x`").cast(DoubleType()).alias("coord_x"),
    col("`playerCoordinates.y`").cast(DoubleType()).alias("coord_y"),
    col("shotType").alias("shot_type"),
    col("situation").alias("situation"),
    col("bodyPart").alias("body_part"),
    col("goalType").alias("result"),
)

df_shots.printSchema()

# drop rows that idk the player_id or match_id or shot_id or the coordinates of the shot
df_shots = df_shots.dropna(
    subset=["player_id", "match_id", "shot_id", "coord_x", "coord_y"]
)

# fill missing values
df_shots = df_shots.fillna(
    {
        "added_time": 0,
        "result": "no-goal",
    }
)

# remove duplicates
df_shots = df_shots.dropDuplicates(["shot_id"])

# verify if exists any rule to apply in the text of this columns
df_shots.select("result").distinct().show()
df_shots.select("situation").distinct().show()
df_shots.select("shot_type").distinct().show()
df_shots.select("body_part").distinct().show()
df_shots.select("shot_minute").distinct().show()
df_shots.select("added_time").distinct().show()

# data validation
null_shots = df_shots.filter(col("shot_id").isNull()).count()
null_matches = df_shots.filter(col("match_id").isNull()).count()
null_players = df_shots.filter(col("player_id").isNull()).count()
null_coords = df_shots.filter(col("coord_x").isNull() | col("coord_y").isNull()).count()
print(f"Null shots: {null_shots}, Null matches: {null_matches}, Null players: {null_players}, Null coordinates: {null_coords}")

invalid_xg = df_shots.filter(
    (col("xg") < 0) | (col("xg") > 1)
).count()

invalid_xgot = df_shots.filter(
    (col("xgot") < 0) | (col("xgot") > 1)
).count()

invalid_coordinates = df_shots.filter(
    (col("coord_x") < 0) |
    (col("coord_x") > 100) |
    (col("coord_y") < 0) |
    (col("coord_y") > 100)
).count()

print(f"Invalid xg: {invalid_xg}, Invalid xgot: {invalid_xgot}, Invalid coordinates: {invalid_coordinates}")

# write the trusted shots data to parquet
df_shots.write.mode("overwrite").parquet("../../data/trusted/shots")

spark.stop()
