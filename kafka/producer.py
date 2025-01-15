import time
import random
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Itinéraire pour un seul véhicule (Casablanca → Marrakech)
route = [(33.5731, -7.5898), (31.6295, -7.9811)]  # Coordonnées GPS

def interpolate_points(coord1, coord2, num_points=30):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return [
        (lat1 + (lat2 - lat1) * i / num_points, lon1 + (lon2 - lon1) * i / num_points)
        for i in range(num_points + 1)
    ]

def generate_gps_data():
    points = interpolate_points(route[0], route[1], 60)
    current_position = 0

    while True:
        if current_position >= len(points):
            current_position = 0  # Réinitialiser le trajet

        point = points[current_position]
        gps_data = {
            'vehicle_id': 'vehicle_1',
            'latitude': round(point[0], 6),
            'longitude': round(point[1], 6),
            'speed': round(random.uniform(70, 90), 2),
            'timestamp': round(time.time(), 2)
        }
        producer.send('gps_data', gps_data)
        print(f"Sent: {gps_data}")
        current_position += 1
        time.sleep(5)

generate_gps_data()
