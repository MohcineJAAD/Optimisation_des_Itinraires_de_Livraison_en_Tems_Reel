import sys
import os

# Ajouter le chemin de base du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from optimizer.route_optimizer import Graph
import happybase
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import json

# Configuration
HBASE_HOST = "localhost"
TABLE_NAME = "gps_data"

spark = SparkSession.builder.appName("StreamingGPS").getOrCreate()
kafka_topic = "gps_data"
kafka_bootstrap_servers = "localhost:9092"

schema = StructType([
    StructField("vehicle_id", StringType(), True),
    StructField("latitude", DoubleType(), True),
    StructField("longitude", DoubleType(), True),
    StructField("speed", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

graph = Graph()

def save_to_hbase(batch):
    connection = happybase.Connection(HBASE_HOST)
    table = connection.table(TABLE_NAME)
    with table.batch() as batch_writer:
        for row in batch:
            row_key = f"{row['vehicle_id']}_{row['timestamp'].replace('.', '_')}"
            batch_writer.put(row_key, {
                b'vehicle_info:latitude': str(row['latitude']),
                b'vehicle_info:longitude': str(row['longitude']),
                b'vehicle_info:speed': str(row['speed']),
                b'vehicle_info:timestamp': row['timestamp'],
                b'vehicle_info:optimized_path': json.dumps(row['optimized_path']),
                b'vehicle_info:optimized_distance': str(row['optimized_distance'])
            })

def process_batch(batch_df, batch_id):
    batch_data = batch_df.collect()
    processed_data = []

    for row in batch_data:
        start_coords = (row.latitude, row.longitude)
        end_coords = (30.4210, -9.5981)  # Exemple : Agadir
        path, distance = graph.get_route(start_coords, end_coords)
        print(f"Chemin optimisé calculé : {path}, Distance : {distance}")

        if path:
            processed_data.append({
                "vehicle_id": row.vehicle_id,
                "latitude": row.latitude,
                "longitude": row.longitude,
                "speed": row.speed,
                "timestamp": row.timestamp,
                "optimized_path": path,
                "optimized_distance": distance
            })

    if processed_data:
        save_to_hbase(processed_data)

stream = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
    .option("startingOffsets", "latest") \
    .load()

parsed_stream = stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

query = parsed_stream.writeStream.foreachBatch(process_batch).start()
query.awaitTermination()
