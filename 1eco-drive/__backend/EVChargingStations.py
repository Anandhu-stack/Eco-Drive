import requests

class EVChargingStations:
    def __init__(self, api_key):
        self.api_key = api_key

    def charge_stations_api(self, latitude, longitude, max_results=10, distance=10):  
        # Construct the API URL
        charge_api = "0a679e06-9fa6-4b80-83e1-8abb7f83a6e9"
        charge_url = f"{charge_api}?key={self.api_key}&latitude={latitude}&longitude={longitude}&maxresults={max_results}&distance={distance}&distanceunit=KM"

        # Send request
        s = requests.Session()
        charge_json = s.get(charge_url).json()

        # Process response
        self.charge_json_status = "OK" if charge_json else "No Data"
        self.charge_stations = []

        if self.charge_json_status == "OK":
            for station in charge_json:
                station_info = {
                    "Name": station.get("AddressInfo", {}).get("Title", "Unknown"),
                    "Address": station.get("AddressInfo", {}).get("AddressLine1", "No address"),
                    "Latitude": station.get("AddressInfo", {}).get("Latitude"),
                    "Longitude": station.get("AddressInfo", {}).get("Longitude"),
                    "Usage Type": station.get("UsageType", {}).get("Title", "Unknown"),
                    "Status": station.get("StatusType", {}).get("Title", "Unknown"),
                    "Number of Connections": len(station.get("Connections", []))
                }
                self.charge_stations.append(station_info)
        else:
            self.charge_stations = "N/A"

        return self.charge_json_status, self.charge_stations
