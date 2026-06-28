// components/chat/ItineraryMap.tsx
'use client';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { MapLocation } from '@/types';
import { useState, useEffect } from 'react';

// Fix default marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface ItineraryMapProps {
  locations: MapLocation[];
}

export default function ItineraryMap({ locations }: ItineraryMapProps) {
  const [routeCoords, setRouteCoords] = useState<[number, number][]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!locations || locations.length < 2) {
      setRouteCoords([]);
      return;
    }

    const sorted = [...locations].sort((a, b) => a.day - b.day);
    const fetchRoutes = async () => {
      setLoading(true);
      const allCoords: [number, number][] = [];

      for (let i = 0; i < sorted.length - 1; i++) {
        const from = sorted[i];
        const to = sorted[i + 1];
        // OSRM expects lng,lat format
        const url = `https://router.project-osrm.org/route/v1/driving/${from.lng},${from.lat};${to.lng},${to.lat}?geometries=geojson&overview=full`;

        try {
          const res = await fetch(url);
          const data = await res.json();
          if (data.code === 'Ok' && data.routes.length > 0) {
            const coords = data.routes[0].geometry.coordinates.map((c: [number, number]) => [c[1], c[0]] as [number, number]);
            allCoords.push(...coords);
          } else {
            // Fallback to straight line for this segment
            allCoords.push([from.lat, from.lng], [to.lat, to.lng]);
          }
        } catch (error) {
          console.warn('Routing failed, using straight line:', error);
          allCoords.push([from.lat, from.lng], [to.lat, to.lng]);
        }
      }

      // Deduplicate consecutive identical points (if any)
      const uniqueCoords: [number, number][] = [];
      for (const coord of allCoords) {
        if (uniqueCoords.length === 0 || 
            uniqueCoords[uniqueCoords.length-1][0] !== coord[0] || 
            uniqueCoords[uniqueCoords.length-1][1] !== coord[1]) {
          uniqueCoords.push(coord);
        }
      }
      setRouteCoords(uniqueCoords);
      setLoading(false);
    };

    fetchRoutes();
  }, [locations]);

  if (!locations || locations.length === 0) return null;

  const sorted = [...locations].sort((a, b) => a.day - b.day);
  const center = sorted.length > 0 ? [sorted[0].lat, sorted[0].lng] : [28.0, 84.0];

  return (
    <div style={{ height: '400px', width: '100%', borderRadius: '8px', overflow: 'hidden', marginTop: '12px' }}>
      <MapContainer center={center as any} zoom={8} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {loading && (
          <div style={{ position: 'absolute', top: 10, left: 10, background: 'white', padding: '4px 8px', borderRadius: 4, zIndex: 1000 }}>
            Fetching routes...
          </div>
        )}
        {sorted.map((loc, idx) => (
          <Marker key={`${idx}-${loc.day}-${loc.name}`} position={[loc.lat, loc.lng]}>
            <Popup>
              <strong>Day {loc.day}</strong><br />
              {loc.name}<br />
              {loc.description && <em>{loc.description}</em>}
            </Popup>
          </Marker>
        ))}
        {routeCoords.length > 0 && (
          <Polyline positions={routeCoords} color="blue" weight={3} />
        )}
      </MapContainer>
    </div>
  );
}