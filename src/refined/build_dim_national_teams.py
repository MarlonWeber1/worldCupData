import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.master("local[*]").appName("WorldCupRefined").getOrCreate()

df = spark.read.parquet("../../data/trusted/national_teams")

df.printSchema()

# create the national teams dimension 
dim_national_teams = df.select(
    col("team_key"),
    col("team_code"),
    col("team_name"),
    col("continent"),
)

# write the refined dim_national_teams data to parquet
dim_national_teams.write.mode("overwrite").parquet("../../data/refined/dim_national_teams")

spark.stop()