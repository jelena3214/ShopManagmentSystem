from pyspark.sql import SparkSession
from pyspark.sql.functions import col, desc, sum
import os
import json


PRODUCTION  = True if ( "PRODUCTION" in os.environ ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ( "DATABASE_IP" in os.environ ) else "localhost"


builder = SparkSession.builder.appName ( "Category statistics" )

if ( not PRODUCTION ):
    builder = builder.master ( "local[*]" )\
                    .config (
                        "spark.driver.extraClassPath",
                        "mysql-connector-j-8.0.33.jar"
                    )

    
spark = builder.getOrCreate ( )

spark.sparkContext.setLogLevel("ERROR")

# Read tables into DataFrames
category_df = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.category" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

item_category_df = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.item_category" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

order_item_df = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.order_item" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

order_df = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/store" ) \
    .option ( "dbtable", "store.order" ) \
    .option ( "user", "root" ) \
    .option ( "password", "123" ) \
    .load ( )

joined_df = order_item_df.join(order_df, order_item_df.order_id == order_df.id) \
    .where(order_df.status == "COMPLETE") \
    .join(item_category_df, order_item_df.item_id == item_category_df.item_id)

# Group by category_id and sum the quantity
delivered_items_df = joined_df.groupBy(item_category_df.category_id) \
    .agg(sum(col("quantity")).alias("total_delivered"))

# Join category_df with delivered_items_df to get the category names
result_df = category_df.join(delivered_items_df, category_df.id == delivered_items_df.category_id, "left") \
    .orderBy(desc("total_delivered"), "name")


print("=== START RESULT ===")
result = result_df.select("name").collect()
dict_list = [row.asDict() for row in result]
result_json = json.dumps(dict_list, indent=4)
print(result_json, flush=True)
print("=== END RESULT ===")
spark.stop()