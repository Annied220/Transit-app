# Group 3 -
    # Isabele DeSouza
    # Trinh Duong
    # Thatcher Holland
    # Andrew Willard
# MIS310
# Group Project
# Transit API - Closest Stop (Details)


############################################################################################
########      see past code for reference on the GUI map, and other GUI stuff.      ########
############################################################################################


"""
This code gets coordinates from an address and fetches nearby bus stops from the Transit App API.
"""

# Libraries
import requests #https://www.w3schools.com/python/module_requests.asp
from geopy.geocoders import Nominatim # https://geopy.readthedocs.io/en/stable/
# https://stackoverflow.com/questions/60928516/get-address-from-given-coordinate-using-python
# https://geopy.readthedocs.io/en/stable/#module-geopy.geocoders
# https://github.com/DenisCarriere/geocoder/blob/master/README.md
# https://geocoder.readthedocs.io/results.html

from datetime import datetime, UTC, timedelta
# https://docs.python.org/3/library/datetime.html#datetime.datetime

"""
# Other libraries we will use:
import tkinter as tk #importing lib as a var to make life easy.
from tkinter import Entry, Button, Label, StringVar #importing parts of lib to gen vars.
from tkintermapview import TkinterMapView
import threading #maybe
"""

# tries to read API.txt. this is to prevent the API key from being hard coded into program.
def api_key():
    """Reads the API key from a file named 'API.txt'."""
    try:
        with open("API.txt", "r") as file:
            API_KEY = file.read().strip()
            if not API_KEY:
                raise ValueError("API key is empty.")
            return API_KEY
    except (FileNotFoundError, ValueError) as e:
        print(f"[API Key Error] {e}")
        exit()

# because there are 2 APIs that use this, make it a function.
def max_distance():
    """Returns the maximum distance (in meters) to search for bus stops."""
    return 1000 # max = 1500
# we could attach this variable to a sliding bar,
# that sliding bar could change the size of a circle in the GUI map to show radius
# this is an unnecessary addition to the scope - but might be fun

# tries to call geopy
def get_coordinates(place):
    """Uses geopy to get latitude and longitude coordinates for a given place name."""
    try:
        geolocator = Nominatim(user_agent="GetLoc") #https://www.youtube.com/watch?v=mhTkaH2YuAc
        location = geolocator.geocode(place,
            country_codes="us", # Restrict search to the US
            viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)], # Bounding box for Connecticut
            bounded=True # Ensures results stay within the view box
        ) # everything here is learned from the documentation # https://geocoder.readthedocs.io/results.html
        if location:
            # print((location.latitude, location.longitude)) # Debugging. Outputs Lat and Lon.
            # print(location.raw) # Debugging. # full data pull
            return location.latitude, location.longitude # Returns latitude, longitude
    except Exception as e:
        print(f"[Geolocation Error] {e}")
    return None # outputs nothing

#
def get_nearby_bus_stops(lat, lon, stop_filter="Routable", pickup_dropoff_filter="Everything"):
    """Sends GET request to the Transit API to fetch nearby bus stops."""
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": api_key()} # Headers for the request
    params = {  # Parameters to be sent in the API request
        "lat": lat,  # Latitude of the location. REQUIRED
        "lon": lon,  # Longitude of the location. REQUIRED
        "max_distance": max_distance(),
        "stop_filter": stop_filter,
        "pickup_dropoff_filter": pickup_dropoff_filter
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200: #200 code is a successful call per their API docs
            data = response.json()
            #print(data)  #debugging
            stops = data.get("stops", [])
            # Ensure "stops" key exists and is non-empty before accessing
            if not stops:
                print("No nearby bus stops found.")
                return None
            # Find the stop with the smallest distance # https://www.w3schools.com/python/python_lambda.asp
            closest_stop = min(stops, key=lambda stop: stop.get("distance", float("inf")))
            return (
                closest_stop.get("stop_lat"),
                closest_stop.get("stop_lon"),
                closest_stop.get("stop_name"),
            )
        else:
            print(f"[Transit API Error] Status code: {response.status_code}")
    except Exception as e:
        print(f"[API Request Error] {e}")
    return None


def get_routes_at_stop(lat, lon):
    """Fetches route info for a given bus stop location."""
    url = "https://external.transitapp.com/v3/public/nearby_routes"
    headers = {"apiKey": api_key()}
    params = {
        "lat": lat,
        "lon": lon,
        "max_distance": max_distance(),
        "should_update_realtime": True
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("routes", [])
        else:
            print(f"[Route API Error] Status code: {response.status_code}")
    except Exception as e:
        print(f"[Route Request Error] {e}")
    return [] #returns json response list

# user input applied to
def closest_stop_to_input():
    """Gets user input, geocodes it, and returns the closest bus stop's coordinates."""
    while True:
        strUserInputLocation = input("Enter a location (or press Enter to exit): ").strip()
        if not strUserInputLocation:
            invalid_entry_message = "Invalid Entry. Try again."
            print(invalid_entry_message)
            #return invalid_entry_message
            continue
        """ might not work in the GUI """

        coordinates = get_coordinates(strUserInputLocation)
        if coordinates:
            lat, lon = coordinates
            #print(f"Location: {strUserInputLocation} ({lat}, {lon})") # debug
            closest_stop = get_nearby_bus_stops(lat, lon)
            if closest_stop:
                stop_lat, stop_lon, stop_name = closest_stop
                print(f"Closest Bus Stop: {stop_name} ({stop_lat}, {stop_lon})") #WE WANT THIS TO BE A POINT ON THE MAP
                # ASSIGN THESE VARIABLES TO A POINT ON THE MAP.
                return stop_lat, stop_lon
            else:
                print("Could not find any nearby bus stops.")
                no_stops_message = "Could not find any nearby bus stops."
                return no_stops_message
        else:
            print("Invalid location. Please try again.")
            invalid_location_message = "Invalid location. Please try again."
            return invalid_location_message

def main():
    latitude, longitude = closest_stop_to_input() # calls lat and lon from function
    #print(f"latitude: {latitude} longitude: {longitude}") # debug
    routes = get_routes_at_stop(latitude, longitude) #applies the lat and lon to the bus stop route info API
    #print(f"For Stop at {routes}:") # Debug

    # handles no route info at stop.
    if not routes:
        print("No routes found for this stop.")
        no_routes_message = "No routes found for this stop."
        return no_routes_message

    # Collects routes with valid next departures
    upcoming_routes = [] #creates empty list to be referenced later

    for route in routes:
        route_short_name = route.get("route_short_name", "Unknown")
        next_departure_message = None

        for itinerary in route.get("itineraries", []):
            for schedule in itinerary.get("schedule_items", []):
                timestamp = schedule.get("departure_time")
                if timestamp and (next_departure_message is None or timestamp < next_departure_message):
                    next_departure_message = timestamp

        if next_departure_message:
            upcoming_routes.append({
                "route": route_short_name,
                "departure_time": next_departure_message
            })

    # Sort routes by the next departure time # https://www.w3schools.com/python/python_lambda.asp
    upcoming_routes.sort(key=lambda r: r["departure_time"])

    """
    Depending on how our GUI will be set up, below are the various outputs we want to have.
    the Next Departure, Next 3 Departures, Next 5 Departures, and ALL Departures.
    
    I assume we will be going with next 3, and will have a message box pop up that displays all departures.
    """

    # Outputs the next upcoming departure
    #print("\nNext Departure:") #debug
    departure_message_1 = "" # creates a variable for the next departure info to be stored
    for route_info in upcoming_routes[:1]:
        # Convert UTC to EST (-5 hours)
        est_time = datetime.fromtimestamp(route_info["departure_time"], UTC) - timedelta(hours=4)
        formatted_time = est_time.strftime('%I:%M %p') # 12-hour format with AM/PM
        formatted_date = est_time.strftime('%B %d') # %B is the datetime variable for %m written out.
        #print(f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time}") #debug
        departure_message_1 += f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time} \n"
    #print(departure_message_1) #debug

    # Outputs the next 3 upcoming departures
    print("\nNext 3 Departures:")
    departure_message_3 = "" # creates a variable for the next 3 departures info to be stored
    for route_info in upcoming_routes[:3]:
        # Convert UTC to EST (-5 hours)
        est_time = datetime.fromtimestamp(route_info["departure_time"], UTC) - timedelta(hours=4)
        formatted_time = est_time.strftime('%I:%M %p') # 12-hour format with AM/PM
        formatted_date = est_time.strftime('%B %d') # %B is the datetime variable for %m written out.
        #print(f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time}")
        departure_message_3 += f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time} \n"
    print(departure_message_3) #debug
    """ reference variable 'departure_message_3' in main GUI """

    # Outputs the next 5 upcoming departures
    #print("\nNext 5 Departures:") # debug
    departure_message_5 = ""  # creates a variable for the next 5 departures info to be stored
    for route_info in upcoming_routes[:5]:
        # Convert UTC to EST (-5 hours)
        est_time = datetime.fromtimestamp(route_info["departure_time"], UTC) - timedelta(hours=4)
        formatted_time = est_time.strftime('%I:%M %p') # 12-hour format with AM/PM
        formatted_date = est_time.strftime('%B %d') # %B is the datetime variable for %m written out.
        #print(f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time}")
        departure_message_5 += f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time} \n"
    #print(departure_message_5)  # debug

    # Outputs ALL upcoming departures
    print("\nAll Departures:")
    departure_message_all = "" # creates a variable for the all departures info to be stored
    for route_info in upcoming_routes[:-1]:
        # Convert UTC to EST (-5 hours)
        est_time = datetime.fromtimestamp(route_info["departure_time"], UTC) - timedelta(hours=4)
        formatted_time = est_time.strftime('%I:%M %p') # 12-hour format with AM/PM
        formatted_date = est_time.strftime('%B %d') # %B is the datetime variable for %m written out.
        #print(f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time}")
        departure_message_all += f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time} \n"
    print(departure_message_all)  # debug
    """ 
    reference variable 'departure_message_all' in main GUI, create a messagebox pop up that displays all departures 
    """

if __name__ == "__main__":
    #add a clock for the current time.
    # sort the outputs by the time and what is coming up.
    main()

"""
# I did add a countdown timer to one of the old codes that is broken that we can use reference the time variable
# within the departure_message_1 and add a countdown clock to the GUI.

Old broken code that does not work with the above code.

# Countdown to next bus
def countdown_timer(arrival_time):
    def update_timer():
        while True:
            remaining = arrival_time - datetime.now(timezone.utc)
            if remaining.total_seconds() <= 0:
                countdown_var.set("Arriving Now")
                break
            countdown_var.set(str(remaining).split('.')[0])
            root.update()
    threading.Thread(target=update_timer, daemon=True).start()
# timer is broken.
# maybe we can make it so the user clicks on ONE route and the countdown time works for that one route.

need to turn all print statements into a variables to be displayed in a label within the GUI.
"""

# Thanks for all the fish.
