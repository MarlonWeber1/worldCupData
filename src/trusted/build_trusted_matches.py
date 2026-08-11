import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, substring_index
from pyspark.sql.types import IntegerType

spark = SparkSession.builder.master("local[*]").appName("WorldCupTrusted").getOrCreate()

df = spark.read.csv("../../data/raw/raw_matches.csv", header=True, inferSchema=False)

df.printSchema()

df_matches = df.select(
    col("id").cast(IntegerType()).alias("match_id"),
    col("`tournament.name`").alias("tournament_name"),
    col("`roundInfo.name`").alias("tournament_phase"),
    col("`homeTeam.name`").alias("home_team"),
    col("`awayTeam.name`").alias("away_team"),
)

df_matches.printSchema()

# verify duplicate match ids
# duplicate ids
duplicate_matches = (
    df_matches.groupBy("match_id").count().filter(col("count") > 1).count()
)

print(f"Duplicate match IDs: {duplicate_matches}")

# verify tournament phases
df_matches.select("tournament_phase").distinct().show()

# fill missing values
df_matches = df_matches.fillna(
    {
        "tournament_phase": "Group Stage",
    }
)

# rewrite the tournament name
df_matches = df_matches.withColumn(
    "tournament_name", substring_index(col("tournament_name"), ",", 1)
)

# data validation
null_ids = df_matches.filter(col("match_id").isNull()).count()
invalid_teams = df_matches.filter(col("home_team") == col("away_team")).count()
invalid_ids = df_matches.filter(col("match_id") <= 0).count()

print(f"Number of null match IDs: {null_ids}")
print(f"Invalid teams: {invalid_teams}")
print(f"Invalid match ids: {invalid_ids}")

# write the trusted matches data to parquet
df_matches.write.mode("overwrite").parquet("../../data/trusted/matches")

spark.stop()
