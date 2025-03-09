import React, { useState } from 'react';
import { MapPin, Battery, ArrowRight } from 'lucide-react';

interface InputFormProps {
  onSubmit: (data: {
    origin: string;
    destination: string;
    batteryCapacity: number;
    currentCharge: number;
  }) => void;
  loading: boolean;
}

const InputForm: React.FC<InputFormProps> = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    batteryCapacity: 50,
    currentCharge: 45,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'batteryCapacity' || name === 'currentCharge' 
        ? parseFloat(value) 
        : value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const chargePercentage = (formData.currentCharge / formData.batteryCapacity) * 100;
  const batteryLevelClass = 
    chargePercentage < 20 ? 'battery-low' : 
    chargePercentage < 50 ? 'battery-medium' : '';

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Origin Address
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MapPin className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            name="origin"
            value={formData.origin}
            onChange={handleChange}
            placeholder="Enter starting location"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Destination Address
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MapPin className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            name="destination"
            value={formData.destination}
            onChange={handleChange}
            placeholder="Enter destination"
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Battery Capacity (kWh)
          </label>
          <input
            type="number"
            name="batteryCapacity"
            value={formData.batteryCapacity}
            onChange={handleChange}
            min="1"
            max="200"
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Current Charge (kWh)
          </label>
          <input
            type="number"
            name="currentCharge"
            value={formData.currentCharge}
            onChange={handleChange}
            min="0"
            max={formData.batteryCapacity}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-sm font-medium text-gray-700 flex items-center">
            <Battery className="h-5 w-5 mr-1 text-gray-500" />
            Current Charge Level
          </span>
          <span className="text-sm font-medium text-gray-700">
            {Math.round(chargePercentage)}%
          </span>
        </div>
        <div className="battery-indicator">
          <div 
            className={`battery-level ${batteryLevelClass}`} 
            style={{ width: `${chargePercentage}%` }}
          ></div>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className={`w-full flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
          loading ? 'opacity-70 cursor-not-allowed' : ''
        }`}
      >
        {loading ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Calculating Route...
          </>
        ) : (
          <>
            Find Optimal Route <ArrowRight className="ml-2 h-4 w-4" />
          </>
        )}
      </button>
    </form>
  );
};

export default InputForm;