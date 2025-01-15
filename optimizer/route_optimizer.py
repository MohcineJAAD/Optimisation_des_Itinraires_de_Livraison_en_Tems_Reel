import requests
class Graph:
    def __init__(self):
        self.base_url = "http://localhost:8989/route"

    def get_route(self, start_coords, end_coords):
        """
        Interroge GraphHopper pour obtenir un itinéraire optimisé entre deux points.
        :param start_coords: Tuple (latitude, longitude) du point de départ.
        :param end_coords: Tuple (latitude, longitude) du point d'arrivée.
        :return: Liste des coordonnées GPS de l'itinéraire, distance totale en km.
        """
        params = {
            "point": [f"{start_coords[0]},{start_coords[1]}", f"{end_coords[0]},{end_coords[1]}"],
            "profile": "car",  # Utilisez 'profile' au lieu de 'vehicle'
            "locale": "fr",
            "points_encoded": "false"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "paths" in data and len(data["paths"]) > 0:
                coordinates = data["paths"][0]["points"]["coordinates"]
                distance = data["paths"][0]["distance"] / 1000  # Distance en kilomètres
                return coordinates, distance
        print(f"Erreur GraphHopper: {response.status_code}, {response.text}")
        return None, None
