// Initialiser la carte Leaflet centrée sur le Maroc
const map = L.map('map').setView([31.7917, -7.0926], 6);

// Ajouter les tuiles OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Icône personnalisée pour le véhicule
const vehicleIcon = L.icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/149/149059.png',
  iconSize: [24, 24],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12]
});

// Conteneur pour le marqueur et la polyline
let vehicleMarker = null;
let polyline = null;

// **Variables pour le tableau de bord**
const connectionStatus = document.getElementById('connection-status');
const vehicleCount = document.getElementById('vehicle-count');

// **Fonction pour mettre à jour le tableau de bord**
function updateDashboard(data) {
  const vehicles = Object.keys(data); // Liste des véhicules
  const speeds = vehicles.map(v => data[v][data[v].length - 1]?.speed || 0); // Récupération des vitesses

  vehicleCount.textContent = vehicles.length; // Nombre de véhicules
  connectionStatus.textContent = "Connecté";
  connectionStatus.classList.add('connected');
  connectionStatus.classList.remove('disconnected');
}

// Fonction pour mettre à jour la carte
function updateMap() {
  fetch(`http://127.0.0.1:5000/api/vehicle_data`)
    .then(response => response.json())
    .then(data => {
      if (data) {
        // **Mettre à jour le tableau de bord**
        updateDashboard(data);

        const vehicleData = data.vehicle; // Données du véhicule unique
        if (vehicleData && vehicleData.length > 0) {
          const vehicleInfo = vehicleData[vehicleData.length - 1]; // Dernière position
          const { latitude, longitude, speed, timestamp, optimized_path } = vehicleInfo;

          // Vérifier les coordonnées valides
          if (!latitude || !longitude) {
            console.warn("Coordonnées invalides :", latitude, longitude);
            return;
          }

          // Mettre à jour le marqueur
          if (!vehicleMarker) {
            vehicleMarker = L.marker([latitude, longitude], { icon: vehicleIcon }).addTo(map);
          } else {
            vehicleMarker.setLatLng([latitude, longitude]);
          }
          vehicleMarker.bindPopup(`
            <b>Véhicule</b><br>
            Vitesse : ${speed.toFixed(2)} km/h<br>
            Dernière mise à jour : ${new Date(Number(timestamp) * 1000).toLocaleString()}
          `).openPopup();

          // Mettre à jour le chemin optimisé
          if (Array.isArray(optimized_path) && optimized_path.length > 0) {
            if (polyline) {
              map.removeLayer(polyline); // Supprimer l'ancienne polyline
            }
            polyline = L.polyline(
              optimized_path.map(coord => [coord[1], coord[0]]), // Inverser [lon, lat] en [lat, lon]
              { color: 'blue', weight: 3, opacity: 0.7 }
            ).addTo(map);
          } else {
            console.warn("Pas de chemin optimisé disponible.");
          }
        } else {
          console.warn("Aucune donnée reçue pour le véhicule.");
        }
      }
    })
    .catch(error => {
      console.error("Erreur lors du chargement des données :", error);
      connectionStatus.textContent = "Déconnecté";
      connectionStatus.classList.add('disconnected');
      connectionStatus.classList.remove('connected');
    });
}

// Mettre à jour la carte et le tableau de bord toutes les 5 secondes
updateMap();
setInterval(updateMap, 5000);
