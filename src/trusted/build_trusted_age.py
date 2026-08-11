import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType

spark = SparkSession.builder.master("local[*]").appName("WorldCupTrusted").getOrCreate()

df = spark.read.csv("../../data/raw/raw_players_age.csv", header=True, inferSchema=False)

df.printSchema()

df_age = df.select(
    col("`player.id`").cast(IntegerType()).alias("player_id"),
    col("age").cast(IntegerType()).alias("age"),
)

df_age.printSchema()

# verify duplicate player ids
duplicate_player_ids = (
    df_age
    .groupBy("player_id")
    .count()
    .filter(col("count") > 1)
    .count()
)

print(f"Duplicate player IDs: {duplicate_player_ids}")

# drop duplicate rows based on player_id
df_age = df_age.dropDuplicates(["player_id"])

# data validation
null_age = df_age.filter(col("age").isNull()).count()
null_player_id = df_age.filter(col("player_id").isNull()).count()

invalid_player_ids = df_age.filter(col("player_id") <= 0).count()
invalid_ages = df_age.filter((col("age") < 15) | (col("age") > 60)).count()

print(f"Null age: {null_age}, Null player_id: {null_player_id}")
print(f"Invalid player IDs: {invalid_player_ids}")
print(f"Invalid ages: {invalid_ages}")

# write the trusted age data to parquet
df_age.write.mode("overwrite").parquet("../../data/trusted/age")

spark.stop()

