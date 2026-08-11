import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, DoubleType

spark = SparkSession.builder.master("local[*]").appName("WorldCupTrusted").getOrCreate()

df = spark.read.csv("../../data/reference/national_teams.csv", header=True, inferSchema=False)

df.printSchema()

df_national_teams = df.select(
    col("team_key").cast(IntegerType()).alias("team_key"),
    col("team_code").alias("team_code"),
    col("team_name").alias("team_name"),
    col("continent").alias("continent"),   
)

df_national_teams.printSchema()

# write the trusted national teams data to parquet
df_national_teams.write.mode("overwrite").parquet("../../data/trusted/national_teams")