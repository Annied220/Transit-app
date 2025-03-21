# No GUI
# need to add more error catching?
#the search function is weak. see about trying to replace GetLoc with something else?

from geopy.geocoders import Nominatim # https://geopy.readthedocs.io/en/stable/
import requests # https://www.w3schools.com/python/module_requests.asp

def get_coordinates(place):
    """Function to get latitude and longitude from an address"""
    geolocator = Nominatim(user_agent="GetLoc") #https://www.youtube.com/watch?v=mhTkaH2YuAc
    location = geolocator.geocode(
        place, # try Robert Vance Residence Hall, type in 'Vance Hall'
        country_codes="us",  # Restrict search to the US
        viewbox=[(42.050587,-73.727775), (40.950943, -71.787220)],  # Bounding box for Connecticut
        bounded=True  # Ensures results stay within the view box
        # everything here is learned from the documentation
    )
    if location:
        #print((location.latitude, location.longitude)) # Debugging. Outputs Lat and Lon.
        #print(location.raw) # Debugging. # full data pull
        return location.latitude, location.longitude # outputs Lat and Long for API use.
    else: return None #"Location not found within Connecticut." # outputs nothing

def get_nearest_bus_stop(lat, lon, api_key, max_distance,
                         stop_filter="Routable", pickup_dropoff_filter="Everything"):
    """Fetch nearby bus stops from API and return the nearest one."""
    if lat is None or lon is None:
        print("Invalid coordinates. Cannot fetch bus stops.")
        return None

    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": api_key}
    params = {
        "lat": lat,
        "lon": lon,
        "max_distance": max_distance,
        "stop_filter": stop_filter,
        "pickup_dropoff_filter": pickup_dropoff_filter
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()

            stops = data.get("stops", [])
            if not stops: print("No bus stops found."); return None
            # Find the nearest stop by distance
            nearest_stop = min(stops, key=lambda stop: stop['distance'])
            return nearest_stop.get("stop_lat"), nearest_stop.get("stop_lon"), nearest_stop.get("stop_name")

            #for key, value in nearest_stop.items():
            #    print(f"{key}: {value}")
            #return nearest_stop # Returns full nearest stop string for debugging

        else: print(f"Error: {response.status_code}"); return None # error catcher
    except Exception as e: print(f"An error occurred: {e}"); return None # error catcher

def main():
    # User Input
    strUserInputLocation = input("Enter a location (try 'Vance Hall' or 'toad's place'): ") # Debug = "Vance Hall"#
    # Assigns returned location.latitude,location.longitude to lat,lon
    latitude , longitude = get_coordinates(strUserInputLocation)

    if latitude is not None and longitude is not None: # if there are values in the these variables from that function
        real_api_key = "[APIKEYHERE]"  # Replace with actual API key
        distance = 1000 # for this GUI, this will be either an input or a sliding bar.
        nearby_bus_stops = get_nearest_bus_stop(latitude, longitude, real_api_key, distance)

        if nearby_bus_stops:
            print("Nearby Bus Stop:", nearby_bus_stops)
    else:
        print("Location not found. Please try again.")

main()
