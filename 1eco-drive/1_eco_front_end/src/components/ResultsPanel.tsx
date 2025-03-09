import React from 'react';
import { Clock, Navigation, Battery, Zap } from 'lucide-react';

interface ResultsPanelProps {
  results: {
    route: any[];
    chargingStations: any[];
    totalDistance: number;
    totalTime: number;
    batteryConsumption: number;
  };
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center">
        <Zap className="mr-2 text-green-600" size={20} />
        Route Results
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center mb-2">
            <Navigation className="text-blue-600 mr-2" size={18} />
            <h3 className="font-medium text-gray-800">Total Distance</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{results.totalDistance} km</p>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center mb-2">
            <Clock className="text-green-600 mr-2" size={18} />
            <h3 className="font-medium text-gray-800">Estimated Time</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{results.totalTime} min</p>
        </div>
        
        <div className="bg-amber-50 p-4 rounded-lg">
          <div className="flex items-center mb-2">
            <Battery className="text-amber-600 mr-2" size={18} />
            <h3 className="font-medium text-gray-800">Battery Usage</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{results.batteryConsumption.toFixed(1)} kWh</p>
        </div>
      </div>
      
      {results.chargingStations.length > 0 && (
        <div>
          <h3 className="font-medium text-gray-800 mb-3 flex items-center">
            <Zap className="text-green-600 mr-2" size={16} />
            Recommended Charging Stops
          </h3>
          
          <div className="space-y-3">
            {results.chargingStations.map((station, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50">
                <h4 className="font-medium text-gray-800">{station.name}</h4>
                <p className="text-sm text-gray-600">{station.address}</p>
                <div className="mt-2 flex items-center">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <Zap className="mr-1" size={12} />
                    Available
                  </span>
                  <span className="ml-2 text-xs text-gray-500">
                    Recommended charging time: 20 min
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h3 className="font-medium text-gray-800 mb-2">Optimization Details</h3>
        <p className="text-sm text-gray-600">
          This route was optimized using Deep Q-Learning to minimize energy consumption while ensuring you reach your destination with sufficient battery charge. The algorithm considers elevation, traffic conditions, and available charging stations.
        </p>
      </div>
    </div>
  );
};

export default ResultsPanel;