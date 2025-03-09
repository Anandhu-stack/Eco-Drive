import React, { useState } from "react";
import { Battery, MapPin, Navigation, Car } from "lucide-react";
import RouteMap from "./components/RouteMap";
import InputForm from "./components/InputForm";
import ResultsPanel from "./components/ResultsPanel";
import "./App.css";

// ✅ Define proper TypeScript types
type RoutePoint = {
  lat: number;
  lng: number;
};

type ChargingStation = {
  name: string;
  location: {
    lat: number;
    lng: number;
  };
  address: string;
};

type APIResponse = {
  route: RoutePoint[];
  chargingStations: ChargingStation[];
  totalDistance: number;
  totalTime: number;
  batteryConsumption: number;
  reward: number;
  time: number;
  charge_num: number;
  SOC: number;
};


function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<APIResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (formData: {
    origin: string;
    destination: string;
    batteryCapacity: number;
    currentCharge: number;
  }) => {
    setLoading(true);
    setError(null);
    setResults(null);
  
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/route?origin=${encodeURIComponent(formData.origin)}&destination=${encodeURIComponent(formData.destination)}`,
        { method: "GET" }
      );
  
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} - ${response.statusText}`);
      }
  
      const data: APIResponse = await response.json();
  
      setResults({
        route: data.route,
        chargingStations: data.chargingStations || [],
        totalDistance: data.totalDistance,  // ✅ Ensure it exists
        totalTime: data.totalTime,          // ✅ Ensure it exists
        batteryConsumption: formData.batteryCapacity * 0.35,  // ✅ Ensure it exists
        reward: data.reward,       // ✅ Include reward
        time: data.time,           // ✅ Include time
        charge_num: data.charge_num, // ✅ Include charge number
        SOC: data.SOC              // ✅ Include SOC
      });
  
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50">
      <header className="bg-white shadow-md py-4">
        <div className="container mx-auto px-4 flex items-center">
          <Battery className="text-green-600 mr-2" size={28} />
          <h1 className="text-2xl font-bold text-gray-800">Eco-Drive</h1>
          <span className="ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
            Optimized EV Routing
          </span>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <MapPin className="mr-2 text-blue-600" size={20} />
              Route Information
            </h2>

            <InputForm onSubmit={handleSubmit} loading={loading} />

            {error && <p className="text-red-600 mt-4">Error: {error}</p>}
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Navigation className="mr-2 text-blue-600" size={20} />
                Route Map
              </h2>

              {loading ? (
                <p className="text-blue-600 text-lg font-semibold">Calculating optimized route...</p>
              ) : (
                <RouteMap
                  route={results?.route || []}
                  chargingStations={results?.chargingStations || []}
                />
              )}
            </div>

            {results && <ResultsPanel results={results} />}
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h3 className="text-lg font-semibold flex items-center">
                <Car className="mr-2" size={20} />
                Eco-Drive
              </h3>
              <p className="text-gray-400 text-sm mt-1">
                Optimized Electric Vehicle Routing with Deep Q-Learning
              </p>
            </div>
            <div className="text-gray-400 text-sm">
              © 2025 Eco-Drive. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;


/*
import React, { useState } from "react";
import { Battery, MapPin, Navigation, Car } from "lucide-react";
import RouteMap from "./components/RouteMap";
import InputForm from "./components/InputForm";
import ResultsPanel from "./components/ResultsPanel";
import "./App.css";


function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<null | {
    route: any[];
    chargingStations: any[];
    totalDistance: number;
    totalTime: number;
    batteryConsumption: number;
  }>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (formData: {
    origin: string;
    destination: string;
    batteryCapacity: number;
    currentCharge: number;
  }) => {
    setLoading(true);
    setError(null);

    try {
      // Request the optimized route from FastAPI
      const response = await fetch(
        `http://127.0.0.1:8000/route?origin=${encodeURIComponent(
          formData.origin
        )}&destination=${encodeURIComponent(formData.destination)}`,
        { method: "GET" }
      );

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const data = await response.json();
      
      // Map API response to frontend format
      setResults({
        route: data.route.map((point: any) => ({
          lat: point.lat,
          lng: point.lng,
        })), // Using actual route data
        chargingStations: data.chargingStations || [], 
        totalDistance: data.reward, 
        totalTime: data.time,
        batteryConsumption: formData.batteryCapacity * 0.35
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50">
      <header className="bg-white shadow-md py-4">
        <div className="container mx-auto px-4 flex items-center">
          <Battery className="text-green-600 mr-2" size={28} />
          <h1 className="text-2xl font-bold text-gray-800">Eco-Drive</h1>
          <span className="ml-2 text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
            Optimized EV Routing
          </span>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <MapPin className="mr-2 text-blue-600" size={20} />
              Route Information
            </h2>

            <InputForm onSubmit={handleSubmit} loading={loading} />

            {error && <p className="text-red-600 mt-4">Error: {error}</p>}
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Navigation className="mr-2 text-blue-600" size={20} />
                Route Map
              </h2>

              <RouteMap
                route={results?.route || []}
                chargingStations={results?.chargingStations || []}
              />
            </div>

            {results && <ResultsPanel results={results} />}
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <h3 className="text-lg font-semibold flex items-center">
                <Car className="mr-2" size={20} />
                Eco-Drive
              </h3>
              <p className="text-gray-400 text-sm mt-1">
                Optimized Electric Vehicle Routing with Deep Q-Learning
              </p>
            </div>
            <div className="text-gray-400 text-sm">
              © 2025 Eco-Drive. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
*/