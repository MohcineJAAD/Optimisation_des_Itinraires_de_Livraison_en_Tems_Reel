from kafka import KafkaConsumer
import json

# Kafka configuration
TOPIC = 'gps-data'
BROKER = 'localhost:9092'

# Initialize Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BROKER,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

# Read messages
for message in consumer:
    print(f"Consumed: {message.value}")

