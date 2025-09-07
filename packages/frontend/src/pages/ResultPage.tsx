import { useMovingStore } from '../stores/movingStore';
import { useQuery } from '@tanstack/react-query';
import { getRoute } from '../queries/movingApi';
import { MapContainer, TileLayer, Polyline } from 'react-leaflet';
import React from 'react';

export const ResultPage: React.FC = () => {
  const { results, fromZip, toZip } = useMovingStore();
  const { data: route, isLoading } = useQuery({
    queryKey: ['route', fromZip, toZip],
    queryFn: () => getRoute({ fromZip, toZip }),
    enabled: !!fromZip && !!toZip,
  });

  if (!results) return <div>No results yet.</div>;

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <h1>Moving Estimate</h1>
      <p>Price: ${results.price}</p>
      <p>Truck: {results.truckType}</p>
      <p>Helpers: {results.helpersCount}</p>
      {isLoading && <div>Loading route...</div>}
      {route && (
        <MapContainer center={[route.start.lat, route.start.lon]} zoom={10} style={{ height: 300, width: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Polyline positions={route.polyline} />
        </MapContainer>
      )}
    </div>
  );
};
