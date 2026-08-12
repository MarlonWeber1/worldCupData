import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["hadoop.home.dir"] = r"C:\hadoop"
os.environ["PATH"] += os.pathsep + r"C:\hadoop\bin"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = SparkSession.builder.master("local[*]").appName("WorldCupRefined").getOrCreate()

df_lineup = spark.read.parquet("../../data/trusted/lineups")
df_age = spark.read.parquet("../../data/trusted/age")

df_lineup.printSchema()
df_age.printSchema()

# create the player dimension
dim_player = df_lineup.join(df_age, on="player_id", how="left").select(
    col("player_id"),
    col("player_name"),
    col("player_position"),
    col("age"),
).dropDuplicates(["player_id"])

dim_player.printSchema()

# check for null values in the age column
null_age_count = dim_player.filter(col("age").isNull()).count()
print(f"Number of players with null age: {null_age_count}")

# write the refined dim_player data to parquet
dim_player.write.mode("overwrite").parquet("../../data/refined/dim_player")

spark.stop()
