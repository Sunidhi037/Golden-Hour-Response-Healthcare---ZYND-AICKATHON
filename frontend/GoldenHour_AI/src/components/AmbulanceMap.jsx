import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Custom icon definitions
const emergencyIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const ambulanceIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const hospitalIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Component to auto-fit bounds to show all markers
function AutoFitBounds({ positions }) {
  const map = useMap();
  
  useEffect(() => {
    if (positions.length > 0) {
      const bounds = L.latLngBounds(positions);
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [positions, map]);
  
  return null;
}

// Component to animate ambulance movement
function MovingAmbulance({ start, end, speed = 0.001 }) {
  const [position, setPosition] = useState(start);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 1) return 0; // Reset when reached destination
        return prev + speed;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [speed]);

  useEffect(() => {
    // Interpolate position between start and end
    const lat = start.lat + (end.lat - start.lat) * progress;
    const lng = start.lng + (end.lng - start.lng) * progress;
    setPosition({ lat, lng });
  }, [progress, start, end]);

  return (
    <Marker position={position} icon={ambulanceIcon}>
      <Popup>
        🚑 Ambulance en route<br />
        Progress: {Math.round(progress * 100)}%
      </Popup>
    </Marker>
  );
}

export default function AmbulanceMap({ 
  emergencyLocation, 
  hospitalLocation,
  ambulanceStartLocation 
}) {
  // Default locations if not provided
  const emergency = emergencyLocation || { lat: 28.7041, lng: 77.1025 };
  const hospital = hospitalLocation || { lat: 28.7196, lng: 77.0369 };
  const ambulanceStart = ambulanceStartLocation || { lat: 28.7100, lng: 77.0700 };

  // Route: Ambulance → Emergency → Hospital
  const routePoints = [
    [ambulanceStart.lat, ambulanceStart.lng],
    [emergency.lat, emergency.lng],
    [hospital.lat, hospital.lng]
  ];

  // All positions for auto-fitting bounds
  const allPositions = [
    [ambulanceStart.lat, ambulanceStart.lng],
    [emergency.lat, emergency.lng],
    [hospital.lat, hospital.lng]
  ];

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>🚨 Live Ambulance Tracking</h3>
        <div style={styles.legend}>
          <span style={styles.legendItem}>🔴 Emergency</span>
          <span style={styles.legendItem}>🔵 Ambulance</span>
          <span style={styles.legendItem}>🟢 Hospital</span>
        </div>
      </div>

      <MapContainer
        center={[emergency.lat, emergency.lng]}
        zoom={13}
        style={{ height: '500px', width: '100%', borderRadius: '10px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Emergency Location - Red Marker */}
        <Marker position={[emergency.lat, emergency.lng]} icon={emergencyIcon}>
          <Popup>
            <strong>🚨 Emergency Location</strong><br />
            Patient needs immediate help
          </Popup>
        </Marker>

        {/* Hospital Location - Green Marker */}
        <Marker position={[hospital.lat, hospital.lng]} icon={hospitalIcon}>
          <Popup>
            <strong>🏥 Selected Hospital</strong><br />
            Destination for patient
          </Popup>
        </Marker>

        {/* Moving Ambulance - Blue Marker */}
        <MovingAmbulance 
          start={ambulanceStart} 
          end={emergency}
          speed={0.005}
        />

        {/* Route Line - Shows path */}
        <Polyline 
          positions={routePoints}
          color="blue"
          weight={4}
          opacity={0.7}
          dashArray="10, 10"
        />

        {/* Auto-fit all markers in view */}
        <AutoFitBounds positions={allPositions} />
      </MapContainer>

      <div style={styles.info}>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>Distance:</span>
          <span style={styles.infoValue}>~5.2 km</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>ETA:</span>
          <span style={styles.infoValue}>~8 minutes</span>
        </div>
        <div style={styles.infoItem}>
          <span style={styles.infoLabel}>Status:</span>
          <span style={styles.infoValue}>🚨 En Route</span>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#1a1a1a',
    padding: '20px',
    borderRadius: '10px',
    marginTop: '20px'
  },
  header: {
    marginBottom: '15px'
  },
  title: {
    color: '#4CAF50',
    margin: '0 0 10px 0',
    fontSize: '20px'
  },
  legend: {
    display: 'flex',
    gap: '20px',
    fontSize: '14px'
  },
  legendItem: {
    color: '#ccc'
  },
  info: {
    display: 'flex',
    justifyContent: 'space-around',
    marginTop: '15px',
    padding: '15px',
    backgroundColor: '#2a2a2a',
    borderRadius: '8px'
  },
  infoItem: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '5px'
  },
  infoLabel: {
    color: '#888',
    fontSize: '12px'
  },
  infoValue: {
    color: '#4CAF50',
    fontSize: '16px',
    fontWeight: 'bold'
  }
};
