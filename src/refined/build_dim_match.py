import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.master("local[*]").appName("WorldCupRefined").getOrCreate()

df = spark.read.parquet("../../data/trusted/matches")

df.printSchema()

# create the match dimension
dim_match = df.select(
    col("match_id"),
    col("tournament_phase"),
    col("home_team"),
    col("away_team"),
)

# write the refined dim_match data to parquet
dim_match.write.mode("overwrite").parquet("../../data/refined/dim_match")

spark.stop()