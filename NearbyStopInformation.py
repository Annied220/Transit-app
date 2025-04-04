import requests # https://www.w3schools.com/python/module_requests.asp
from geopy.geocoders import Nominatim # https://geopy.readthedocs.io/en/stable/

# get_coordinates
# get_nearby_bus_stops

def api_key():
    """ Reads the API key from a file named 'API.txt'. """
    try:
        with open("API.txt", "r") as file:
            API_KEY = file.read()
            if not API_KEY: raise ValueError("API key is empty")
            return API_KEY # if the file is found, export contents to be called as function
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        exit()

def get_coordinates(place):
    """Uses geopy to get latitude and longitude coordinates for a given place name."""
    geolocator = Nominatim(user_agent="GetLoc") #https://www.youtube.com/watch?v=mhTkaH2YuAc
    location = geolocator.geocode(
        place,
        country_codes="us", # Restrict search to the US
        viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)], # Bounding box for Connecticut
        bounded=True)# Ensures results stay within the view box
        # everything here is learned from the documentation
    if location: 
        #print((location.latitude, location.longitude)) # Debugging. Outputs Lat and Lon.
        #print(location.raw) # Debugging. # full data pull
        return location.latitude, location.longitude  # Returns latitude, longitude
    else: return None  # outputs nothing

def max_distance():
    """Returns the maximum distance (in meters) to search for bus stops. """
    return 1000

def get_nearby_bus_stops(lat, lon, stop_filter="Routable", pickup_dropoff_filter="Everything"):
    """ Sends GET request to the Transit API to fetch nearby bus stops and finds closest stop based on distance."""
    if lat is None or lon is None:
        print("Invalid coordinates. Cannot fetch bus stops.")
        return None

    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": api_key()} # Headers for the request
    params = {  # Parameters to be sent in the API request
        "lat": lat, # Latitude of the location. REQUIRED
        "lon": lon, # Longitude of the location. REQUIRED
        "max_distance": max_distance(),
        "stop_filter": stop_filter,
        "pickup_dropoff_filter": pickup_dropoff_filter
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200: #200 code is a successful call per their API docs
            data = response.json()
            # print(data) #debugging
            stops = data.get("stops", [])
            # Ensure "stops" key exists and is non-empty before accessing
            if not stops:
                print("No bus stops found.")
                return None

            # Find the stop with the smallest distance
            closest_stop = min(stops, key=lambda stop: stop.get("distance", float("inf")))
            
            stop_lat = closest_stop.get("stop_lat")
            stop_lon = closest_stop.get("stop_lon")
            stop_name = closest_stop.get("stop_name")
            stop_distance = closest_stop.get("distance")

            # print(f"Closest Stop: {stop_name} ({stop_distance} meters away)") # debug
            return stop_lat, stop_lon, stop_name
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    """ Main function to get user input, geocode it, and print the closest bus stop. """
    strUserInputLocation = input("Enter a location (try 'Vance Hall'): ")
    coordinates = get_coordinates(strUserInputLocation)

    if coordinates:
        lat, lon = coordinates
        closest_stop = get_nearby_bus_stops(lat, lon)
        if closest_stop: print("Closest Bus Stop Info:", closest_stop)
    else: print("Location not found. Please try again.")

# Only run the program if this file is executed directly
if __name__ == "__main__": main()
