from datetime import datetime
import urllib.parse
import requests
from haversine import haversine
from battery import lithium_ion_battery
from motor import need_energy
import math
import traceback

class environment():
    def __init__(self, origin_adr, destination_adr):
        self.origin = origin_adr
        self.destination = destination_adr
        self.latt = 0
        self.lngg = 0
        self.make_map()
        self.battery = lithium_ion_battery(50000) #Wh
        self.need_energy = need_energy()
        self.charge_num = 0
        self.unreach_position_num = 0
        self.time = 0
        self.ii = 0
        self.status_dir_check = 0
        self.length = 1
        self.envheightkm = 1
        

    def geocoding_api(self, address):  # 2 output: status, position
        # address: key word of place
        geocode_api = 'pk.47e21dac251393c0ceb955d6836a190e'
        
        # Use the provided address parameter instead of hardcoded value
        encoded_address = urllib.parse.quote(address)
        geocode_url = f'https://us1.locationiq.com/v1/search?key={geocode_api}&q={encoded_address}&format=json'
        
        s = requests.Session()
        try:
            response = s.get(geocode_url)
            response.raise_for_status()
            geocode_json = response.json()
            print("DEBUG: Geocode JSON Response:", geocode_json)
            
            # LocationIQ returns a list of results, not a status object
            if isinstance(geocode_json, list) and len(geocode_json) > 0:
                self.geocode_json_status = "OK"
                first_result = geocode_json[0]
                
                # Extract latitude and longitude
                latt = float(first_result.get('lat', 0))
                lngg = float(first_result.get('lon', 0))
                
                self.latt = latt
                self.lngg = lngg
                self.geoposition = f"{latt},{lngg}"
                self.geoposition_tuple = (latt, lngg)
                
                return self.geocode_json_status, self.geoposition, self.geoposition_tuple
            else:
                self.geocode_json_status = "ZERO_RESULTS"
                self.geoposition = 'N/A'
                self.geoposition_tuple = ('g', 'g')
                return self.geocode_json_status, self.geoposition, self.geoposition_tuple
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Geocoding request failed - {e}")
            self.geocode_json_status = "REQUEST_DENIED"
            self.geoposition = 'N/A'
            self.geoposition_tuple = ('g', 'g')
            return self.geocode_json_status, self.geoposition, self.geoposition_tuple

    def elevation_api(self, location):  # 2 output: elevation, resolution
        # location = '51.4700223,-0.4542955'
        
        # Parse the location into lat,lon format
        if "," not in location:
            print("ERROR: Location is not in 'lat,lon' format!")
            return "ERROR", "N/A"
            
        lat, lon = location.split(",")
        
        # Open-Elevation API expects a POST request with JSON payload
        elevation_url = "https://api.open-elevation.com/api/v1/lookup"
        payload = {
            "locations": [
                {
                    "latitude": float(lat),
                    "longitude": float(lon)
                }
            ]
        }
        
        try:
            s = requests.Session()
            response = s.post(elevation_url, json=payload)
            response.raise_for_status()
            elevation_json = response.json()
            
            if "results" in elevation_json and len(elevation_json["results"]) > 0:
                self.elevation_json_status = "OK"
                self.elevation_data_results_elevation = elevation_json["results"][0]["elevation"]
                elevation_data_results_resolution = 30  # Default resolution for open-elevation
                return self.elevation_json_status, self.elevation_data_results_elevation
            else:
                self.elevation_json_status = "NO_RESULTS"
                self.elevation_data_results_elevation = 'N/A'
                return self.elevation_json_status, self.elevation_data_results_elevation
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Elevation request failed - {e}")
            self.elevation_json_status = "REQUEST_DENIED"
            self.elevation_data_results_elevation = 'N/A'
            return self.elevation_json_status, self.elevation_data_results_elevation

    def directions_api(self, origin, destination):
        """Fetches driving directions between two locations using the LocationIQ API."""

        print(f"DEBUG: Origin received in directions_api: {origin}")
        print(f"DEBUG: Destination received in directions_api: {destination}")

        # Validate input
        if not origin or not destination:
            print("ERROR: One of the locations is missing!")
            return None, None, None

        if "," not in origin or "," not in destination:
            print("ERROR: Origin or destination is not in 'lat,lon' format!")
            return None, None, None

        # Parse latitude and longitude
        try:
            origin_lat, origin_lon = origin.split(",")
            destination_lat, destination_lon = destination.split(",")
            
            # Convert to float to validate format
            float(origin_lat), float(origin_lon)
            float(destination_lat), float(destination_lon)
        except (ValueError, TypeError):
            print("ERROR: Invalid coordinate format received.")
            return None, None, None

        # Convert to 'lon,lat' format required by the API
        origin_fixed = f"{origin_lon},{origin_lat}"
        destination_fixed = f"{destination_lon},{destination_lat}"

        # LocationIQ API Key
        directions_api_key = "pk.47e21dac251393c0ceb955d6836a190e"

        # Construct API request URL
        directions_url = (
            f"https://us1.locationiq.com/v1/directions/driving/{origin_fixed};{destination_fixed}"
            f"?key={directions_api_key}&alternatives=false&steps=true&geometries=geojson&overview=full&annotations=true"
        )

        print(f"DEBUG: Requesting directions from API: {directions_url}")

        # Make API request
        try:
            response = requests.get(directions_url)
            response.raise_for_status()  # Raise an error for HTTP status codes
            directions_json = response.json()
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request failed - {e}")
            return None, None, None

        # Validate response structure
        if not directions_json.get("routes"):
            print("ERROR: No valid routes found in the API response.")
            return None, None, None

        # Extract route details
        try:
            directions_data_routes = directions_json["routes"][0]
            directions_data_routes_legs = directions_data_routes.get("legs", [])

            if not directions_data_routes_legs:
                print("ERROR: No route legs found in the response.")
                return None, None, None

            # Correctly handle steps structure from LocationIQ API
            self.directions_data_routes_legs_steps = []
            for leg in directions_data_routes_legs:
                steps = leg.get("steps", [])
                for step in steps:
                    # Build step structure similar to Google Maps API for compatibility
                    maneuver = step.get("maneuver", {})
                    location = maneuver.get("location", [0, 0])
                    
                    # LocationIQ returns [lon, lat] while we need [lat, lon]
                    start_location = {
                        "lat": location[1],
                        "lng": location[0]
                    }
                    
                    # Get the end location from the next step or use destination for last step
                    if "next" in step and "maneuver" in step["next"]:
                        next_location = step["next"]["maneuver"].get("location", [0, 0])
                        end_location = {
                            "lat": next_location[1],
                            "lng": next_location[0]
                        }
                    else:
                        # For the last step, use the destination
                        end_location = {
                            "lat": float(destination_lat),
                            "lng": float(destination_lon)
                        }
                    
                    # Extract distance and duration
                    distance_value = step.get("distance", 0)
                    duration_value = step.get("duration", 0)
                    
                    structured_step = {
                        "start_location": start_location,
                        "end_location": end_location,
                        "distance": {"value": distance_value},
                        "duration": {"value": duration_value}
                    }
                    
                    self.directions_data_routes_legs_steps.append(structured_step)

            # Extract route boundaries from maneuver locations
            latitudes = [step["maneuver"]["location"][1] for leg in directions_data_routes_legs for step in leg.get("steps", [])]
            longitudes = [step["maneuver"]["location"][0] for leg in directions_data_routes_legs for step in leg.get("steps", [])]
            
            if not latitudes or not longitudes:
                print("ERROR: No coordinate data found in the steps.")
                return None, None, None

            self.bound = {
                "north": max(latitudes),
                "east": max(longitudes),
                "south": min(latitudes),
                "west": min(longitudes),
            }

            self.directions_json_status = "OK"  # Mark as successful
            return self.directions_json_status, self.directions_data_routes_legs_steps, self.bound

        except (KeyError, IndexError) as e:
            print(f"ERROR: Unexpected data structure in API response - {e}")
            return None, None, None

    def chargingstation_api(self, latitude, longitude, max_results=10, distance=10):
        charge_api = "0a679e06-9fa6-4b80-83e1-8abb7f83a6e9"
        charge_url = f"https://api.openchargemap.io/v3/poi/?key={charge_api}&latitude={latitude}&longitude={longitude}&maxresults={max_results}&distance={distance}&distanceunit=KM"
        s = requests.Session()
        try:
            charge_json = s.get(charge_url).json()
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
        except requests.exceptions.RequestException as e:
            return "Request Error", str(e)

    def make_map(self):
        print("DEBUG: Entering make_map()")
        origin_status, origin_position, origin_position_num = self.geocoding_api(self.origin)
        print("DEBUG: Exiting make_map()")
        if origin_position_num == ('g','g'):
            origin_position_num = (self.latt, self.lngg)
        destination_status, destination_position, destination_position_num= self.geocoding_api(self.destination)
        if destination_position_num == ('g','g'):
            destination_position_num = (self.latt, self.lngg)

        direction_status, direction_step, self.map_bound = self.directions_api(origin_position, destination_position)
        self.Google_step = direction_step
        
        # Retry up to 3 times if directions API fails
        retry_count = 0
        while direction_status != 'OK' and retry_count < 3:
            print(f"Retrying directions API, attempt {retry_count + 1}")
            direction_status, direction_step, self.map_bound = self.directions_api(origin_position, destination_position)
            retry_count += 1
            
        if direction_status != 'OK':
            print("WARNING: Could not get directions after multiple attempts")
            
        self.current_position = origin_position_num  # position tuple (lat,lng)
        self.start_position = origin_position_num # position tuple (lat,lng)
        self.end_position = destination_position_num # position tuple (lat,lng)

    def stride_length(self, position):
        start_lat = self.start_position[0]
        start_lng = self.start_position[1]
        end_lat = self.end_position[0]
        end_lng = self.end_position[1]
        east = start_lng if start_lng > end_lng else end_lng
        west = start_lng if start_lng < end_lng else end_lng
        north = start_lat if start_lat > end_lat else end_lat
        south = start_lat if start_lat < end_lat else end_lat
        a = (north, west)
        b = (south, west)
        self.stridebounda = a
        self.strideboundb = b
        lat = position[0]
        #lng = position[1]
        right = (lat, east)
        left = (lat, west)
        height = haversine(a, b) # km
        self.envheightkm = height
        wide = haversine(right, left) # km
        self.stride_height = (north - south) / (height * self.length)  # positive   # 500m per stride
        self.stride_wide = (east - west) / (wide * self.length)

    def step(self, action):  # output:
        # action is in the set of (0,1,2,3) = (north, east, south, west)
        # self.current_position is tuple (lat, lng)
        self.step_reward = 0
        current_status = False
        step_history = []
        
        self.stride_length(self.current_position)
        stride_direction = -1 if action > 1 else 1
        if action == 0:  # north
            self.next_position = (self.current_position[0] + stride_direction * self.stride_height, self.current_position[1])
        if action == 1:  # east
            self.next_position = (self.current_position[0], self.current_position[1] + stride_direction * self.stride_wide)
        if action == 2:  # south
            self.next_position = (self.current_position[0] + stride_direction * self.stride_height, self.current_position[1])
        if action == 3:  # west
            self.next_position = (self.current_position[0], self.current_position[1] + stride_direction * self.stride_wide)

        current = f"{self.current_position[0]},{self.current_position[1]}"
        next_position = f"{self.next_position[0]},{self.next_position[1]}"
        
        # Check if next position is valid
        self.status_dir_check = 0
        status, leg_step, bound = self.directions_api(current, next_position)
        self.status_dir_check = status
        
        # Check if the next position is out of bounds or unreachable
        if (status != 'OK' or 
            self.next_position[0] > self.map_bound['north'] or 
            self.next_position[0] < self.map_bound['south'] or 
            self.next_position[1] > self.map_bound['east'] or 
            self.next_position[1] < self.map_bound['west']):
            
            # The step is not reachable
            if status != 'OVER_QUERY_LIMIT':
                self.step_reward = -1
                self.unreach_position_num = self.unreach_position_num + 1
            self.next_position = self.current_position  # Revert to previous position
        else:
            self.step_reward -= 0.1    # get -0.1 reward for every transition
            
            # Process each step of the leg
            for i in range(len(leg_step)):
                start = (leg_step[i]['start_location']['lat'],leg_step[i]['start_location']['lng'])
                end = (leg_step[i]['end_location']['lat'],leg_step[i]['end_location']['lng'])
                duration = leg_step[i]['duration']['value']  # second
                distance = leg_step[i]['distance']['value']  # km
                start_position = f"{start[0]},{start[1]}"
                end_position = f"{end[0]},{end[1]}"
                
                # Get elevation data
                status, height_start = self.elevation_api(start_position)
                status1, height_end = self.elevation_api(end_position)
                
                retry_count = 0
                while (status != 'OK' or status1 != 'OK') and retry_count < 3:
                    status, height_start = self.elevation_api(start_position)
                    status1, height_end = self.elevation_api(end_position)
                    retry_count += 1
                
                if status != 'OK' or status1 != 'OK':
                    print(f"WARNING: Could not get elevation data after multiple attempts")
                    height_start = 0
                    height_end = 0
                
                elevation = height_end - height_start  # unit: m
                if duration <= 0:
                    duration = 1
                    
                self.time = self.time + duration
                speed = math.sqrt(distance ** 2 + elevation ** 2) / duration  # m/s
                angle = math.atan2(distance * 1000, elevation)   # degree
                angle = angle if angle > 0 else 0
                power = self.need_energy.energy(angle=angle, V=speed)
                energy_consume = 0
                
                # Simulate energy consumption over time
                for t in range(int(duration)):
                    charge = self.battery.use(duration=1, power=power)
                    energy_consume += self.battery.energy_consume
                    self.step_reward -= self.battery.energy_consume/100000
                    if charge:   # this duration need to charge the battery
                        self.charge_num += 1
                        self.battery.charge(50000)    # make it full capacity

                step_history.append([start, end, duration, distance, angle, speed, energy_consume])
            
            # Check if we're close to the destination
            if (abs(self.next_position[0] - self.end_position[0]) < self.stride_height and 
                abs(self.next_position[1] - self.end_position[1]) < self.stride_wide):
                
                self.step_reward = 1   # really close to end position within one step
                self.step_reward -= 0.1
                
                # Calculate the reward between current position to the end
                end_position = f"{self.end_position[0]},{self.end_position[1]}"
                statusE, leg_stepE, boundE = self.directions_api(next_position, end_position)
                self.legE = leg_stepE
                
                if statusE == 'OK':
                    for i in range(len(self.legE)):
                        start = (self.legE[i]['start_location']['lat'], self.legE[i]['start_location']['lng'])
                        end = (self.legE[i]['end_location']['lat'], self.legE[i]['end_location']['lng'])
                        duration = self.legE[i]['duration']['value']  # second
                        distance = self.legE[i]['distance']['value']  # km
                        start_position = f"{start[0]},{start[1]}"
                        end_position = f"{end[0]},{end[1]}"
                        
                        status, height_start = self.elevation_api(start_position)
                        status1, height_end = self.elevation_api(end_position)
                        
                        retry_count = 0
                        while (status != 'OK' or status1 != 'OK') and retry_count < 3:
                            status, height_start = self.elevation_api(start_position)
                            status1, height_end = self.elevation_api(end_position)
                            retry_count += 1
                            
                        if status != 'OK' or status1 != 'OK':
                            print(f"WARNING: Could not get elevation data after multiple attempts")
                            height_start = 0
                            height_end = 0
                            
                        elevation = height_end - height_start  # unit: m
                        if duration <= 0:
                            duration = 1
                            
                        self.time = self.time + duration
                        speed = math.sqrt(distance ** 2 + elevation ** 2) / duration  # m/s
                        angle = math.atan2(distance * 1000, elevation)   # degree
                        angle = angle if angle > 0 else 0   # we let downard as flat
                        power = self.need_energy.energy(angle=angle, V=speed)
                        energy_consume = 0
                        
                        for t in range(duration):
                            charge = self.battery.use(duration=1, power=power)
                            energy_consume += self.battery.energy_consume
                            self.step_reward -= self.battery.energy_consume/100000
                            if charge:   # this duration need to charge the battery
                                self.charge_num += 1
                                self.battery.charge(50000)    # make it full capacity
                current_status = True
                self.current_position = self.start_position

        self.current_step_history = step_history
        self.current_position = self.next_position
        batterySOC = self.battery.SOC
        return self.current_position, self.step_reward, current_status, self.charge_num, batterySOC

    def origine_map_reward(self):  # to get the step_reward, chargenum, SOC, time which the route google provided
        leg = self.Google_step
        step_reward = 0
        time = 0
        
        if not leg:
            print("WARNING: No route steps available")
            return 0, 0, self.battery.SOC, 0
            
        for i in range(len(leg)):
            start = (leg[i]['start_location']['lat'],leg[i]['start_location']['lng'])
            end = (leg[i]['end_location']['lat'],leg[i]['end_location']['lng'])
            duration = leg[i]['duration']['value']  # second
            distance = leg[i]['distance']['value']  # km
            start_position = f"{start[0]},{start[1]}"
            end_position = f"{end[0]},{end[1]}"
            
            status, height_start = self.elevation_api(start_position)
            status1, height_end = self.elevation_api(end_position)
            
            retry_count = 0
            while (status != 'OK' or status1 != 'OK') and retry_count < 3:
                status, height_start = self.elevation_api(start_position)
                status1, height_end = self.elevation_api(end_position)
                retry_count += 1
                
            if status != 'OK' or status1 != 'OK':
                print(f"WARNING: Could not get elevation data after multiple attempts")
                height_start = 0
                height_end = 0
                
            elevation = height_end - height_start  # unit: m
            if duration <= 0:
                duration = 1
                
            time = time + duration
            speed = math.sqrt(distance ** 2 + elevation ** 2) / duration  # m/s
            angle = math.atan2(distance * 1000, elevation)   # degree
            angle = angle if angle > 0 else 0
            power = self.need_energy.energy(angle=angle, V=speed)
            energy_consume = 0
            
            for t in range(int(duration)):
                charge = self.battery.use(duration=1, power=power)
                energy_consume += self.battery.energy_consume
                step_reward -= self.battery.energy_consume/100000
                if charge:   # this duration need to charge the battery
                    self.charge_num += 1
                    self.battery.charge(50000)    # make it full capacity
                    
        chargenum = self.charge_num
        SOC = self.battery.SOC
        self.battery.charge(50000)    # make it full capacity
        self.battery.use(0,0)
        self.charge_num = 0         
        return step_reward, chargenum, SOC, time

    def battery_charge(self):
        self.battery.charge(50000)
        self.battery.use(0,0)

    def battery_condition(self):
        soc = self.battery.SOC
        charge_numm = self.charge_num
        return soc, charge_numm    
