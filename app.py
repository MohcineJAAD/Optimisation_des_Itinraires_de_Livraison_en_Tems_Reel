from flask import Flask, render_template, jsonify
from flask_cors import CORS
import happybase
import json

# Configuration
HBASE_HOST = "localhost"
TABLE_NAME = "gps_data"

# Initialisation de l'application Flask
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
CORS(app)  # Autoriser les requêtes cross-origin


def get_vehicle_data_from_hbase():
    """
    Récupérer les données des véhicules depuis HBase.
    """
    connection = happybase.Connection(HBASE_HOST)
    table = connection.table(TABLE_NAME)
    data = {}

    try:
        for key, row in table.scan():
            # Décodage des informations du véhicule
            vehicle_id, _ = key.decode().split('_', 1)
            latitude = float(row.get(b'vehicle_info:latitude', b'0.0'))
            longitude = float(row.get(b'vehicle_info:longitude', b'0.0'))
            speed = float(row.get(b'vehicle_info:speed', b'0.0'))
            timestamp = row.get(b'vehicle_info:timestamp', b'0').decode()
            optimized_path = json.loads(row.get(b'vehicle_info:optimized_path', b'[]').decode())
            optimized_distance = float(row.get(b'vehicle_info:optimized_distance', b'0.0'))

            if vehicle_id not in data:
                data[vehicle_id] = []

            data[vehicle_id].append({
                "latitude": latitude,
                "longitude": longitude,
                "speed": speed,
                "timestamp": timestamp,
                "optimized_path": optimized_path,
                "optimized_distance": optimized_distance
            })

    except Exception as e:
        print(f"Erreur lors de la récupération des données HBase : {e}")

    finally:
        connection.close()

    return data


@app.route("/api/vehicle_data", methods=["GET"])
def get_vehicle_data():
    """
    API pour récupérer les données des véhicules.
    """
    try:
        data = get_vehicle_data_from_hbase()
        print(f"Données récupérées depuis HBase : {data}")
        return jsonify(data)
    except Exception as e:
        print(f"Erreur lors du traitement de l'API /api/vehicle_data : {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    """
    Point d'entrée principal pour l'application.
    """
    return render_template("index.html")


if __name__ == "__main__":
    # Exécuter le serveur Flask
    app.run(host="0.0.0.0", port=5000, debug=True)
