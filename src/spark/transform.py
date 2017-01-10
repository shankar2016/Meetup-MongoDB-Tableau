from pyspark import SparkContext, SparkConf
from pyspark.sql import HiveContext
import sys
import urllib
import pymongo_spark
import json
from config.mongo_config import *

pymongo_spark.activate()

def main():
    conf = SparkConf().setAppName("transform")
    sc = SparkContext(conf=conf)
    sqlContext = HiveContext(sc)
    conn = "mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/{mongo_db}.{mongo_collection}".format(
        mongo_user=MONGO_USER,
        mongo_pass=urllib.quote_plus(MONGO_PASSWORD),
        mongo_host=MONGO_HOST,
        mongo_port=MONGO_PORT,
        mongo_db=DB_NAME,
        mongo_collection=COLLECTION_NAME)
    rdd = sc.mongoRDD(conn)

    new_rdd = rdd.map(lambda x: dict([(i, x[i]) for i in x if i != '_id'])
                ).map(lambda x: json.dumps(x, ensure_ascii=False).encode('ascii', 'replace')
                ).map(lambda x: "".join(x.split("\\n")))
    df = sqlContext.jsonRDD(new_rdd)
    df.registerTempTable('events_temp')
    sqlContext.sql('DROP TABLE IF EXISTS default.events')
    sqlContext.sql('DROP TABLE IF EXISTS default.clean_table')
    sqlContext.sql('CREATE TABLE events AS SELECT * FROM events_temp')
    sqlContext.sql("CREATE TABLE clean_table AS SELECT description AS event_desc, id AS event_id, yes_rsvp_count, group.category.name AS cat_name, group.category.shortname AS cat_short, group.category.id AS cat_id, group.name AS group_name, group.topics.name AS topic_name, name AS event_name, time AS start_time, utc_offset AS timezone_offset, venue.state AS venue_state, venue.city AS venue_city, venue.zip AS venue_zip, fee.amount AS fee_amt, fee.required AS req_fee FROM events")

if __name__ == "__main__":
    main()
