
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("DemoApp").getOrCreate()
df = spark.read.csv("labs.csv", header=True, inferSchema=True)
df.show()

df.groupBy("TestName").count().show()