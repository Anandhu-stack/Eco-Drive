import React from 'react';
import { MapPin, Zap } from 'lucide-react';

interface RouteMapProps {
  route: Array<{lat: number; lng: number}>;
  chargingStations: Array<{
    name: string;
    location: {lat: number; lng: number};
    address: string;
  }>;
}

const RouteMap: React.FC<RouteMapProps> = ({ route, chargingStations }) => {
  const hasRoute = route && route.length > 0;
  
  return (
    <div className="map-container">
      {!hasRoute ? (
        <div className="text-center">
          <MapPin className="mx-auto h-8 w-8 text-gray-400 mb-2" />
          <p>Enter origin and destination to see the route</p>
        </div>
      ) : (
        <div className="w-full h-full relative">
          {/* This is a placeholder for the actual map implementation */}
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-gray-500">
              Map visualization would be displayed here with the route and charging stations.
            </p>
          </div>
          
          <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Route Legend</h3>
            <div className="flex items-center mb-2">
              <div className="route-point-marker start-marker mr-2"></div>
              <span className="text-xs text-gray-600">Starting Point</span>
            </div>
            <div className="flex items-center mb-2">
              <div className="route-point-marker end-marker mr-2"></div>
              <span className="text-xs text-gray-600">Destination</span>
            </div>
            <div className="flex items-center">
              <div className="mr-2 text-green-500">
                <Zap size={16} />
              </div>
              <span className="text-xs text-gray-600">Charging Station</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RouteMap;