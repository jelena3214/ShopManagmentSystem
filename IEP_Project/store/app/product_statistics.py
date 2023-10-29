from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, sum, coalesce, lit
import os
import json


PRODUCTION  = True if ( "PRODUCTION" in os.environ ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ( "DATABASE_IP" in os.environ ) else "localhost"


builder = SparkSession.builder.appName ( "Product statistics" )

if ( not PRODUCTION ):
    builder = builder.master ( "local[*]" )\
                    .config (
                        "spark.driver.extraClassPath",
                        "mysql-connector-j-8.0.33.jar"
                    )

    
spark = builder.getOrCreate ( )

spark.sparkContext.setLogLevel("ERROR")

order_data_frame = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.order" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

item_data_frame = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.item" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

order_item_data_frame = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.order_item" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

# Perform the left joins
joined_df = item_data_frame.join(order_item_data_frame, item_data_frame.id == order_item_data_frame.item_id, "left") \
    .join(order_data_frame, order_item_data_frame.order_id == order_data_frame.id, "left")

# Calculate the counts for different status values using when and count functions
result = joined_df.groupBy("name") \
    .agg(
        coalesce(sum(when(col("status") != "COMPLETE", col("quantity"))), lit(0)).alias("waiting"), # not completed(created and pending)
        coalesce(sum(when(col("status") == "COMPLETE", col("quantity"))), lit(0)).alias("done")
    )

print("=== START RESULT ===")
#print(result.collect())
result = result.collect()
dict_list = [row.asDict() for row in result]
result_json = json.dumps(dict_list, indent=4)
print(result_json, flush=True)
print("=== END RESULT ===")

spark.stop()