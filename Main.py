# Group 3 -
    # Isabele DeSouza
    # Trinh Duong
    # Thatcher Holland
    # Andrew Willard
# MIS310
# Group Project
# Transit API - Closest Stop (Details)

"""
I am melting. it is bed time.
"""


"""
this code is for the bus stop finder,
it is a tkinter window that allows the user to enter a location and get the nearest bus stop.
it also displays the next bus arrival time.
"""

# Libraries
from geopy.geocoders import Nominatim
import requests
import tkinter as tk #importing lib as a var to make life easy.
from tkinter import Entry, Button, Label, StringVar #importing parts of lib to gen vars.
from tkintermapview import TkinterMapView
import threading
from datetime import datetime, timezone, UTC, timedelta
# https://docs.python.org/3/library/datetime.html#datetime.datetime

# with open("API.txt", "r") as file: API_KEY = file.read() #
# tries to read API.txt. this is to prevent the API key from being hard coded into program.
try:
    with open("API.txt", "r") as file:
        API_KEY = file.read() #.strip()
        if not API_KEY: raise ValueError("API key is empty")
except (FileNotFoundError, ValueError) as e: print(f"Error: {e}"); exit()

#######################################################################################################################

# Initialize Tkinter Window
root = tk.Tk() # calling and initializing tkinter as a variable for reference
root.title("Bus Stop Finder") #window title
root.geometry("700x600") # window size
root.configure(bg="#1E1E1E")  # Dark Mode Background


#######################################################################################################################

# Get latitude and longitude from user input address
def get_coordinates(place):
    geolocator = Nominatim(user_agent="GetLoc")
    location = geolocator.geocode(
        place, country_codes="us", viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)], bounded=True)
    return (location.latitude, location.longitude) if location else None, None

def get_nearest_bus_stop(lat, lon, max_distance=1000):
    """Fetch nearby bus stops from API and return the closest one with its global_stop_id."""
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": API_KEY}
    params = {"lat": lat, "lon": lon, "max_distance": max_distance}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        stops = response.json().get("stops", []) # if output, do the do.
        if not stops: return None, None  # No stops found
        closest_stop = min(stops, key=lambda stop: stop['distance']) # Find the closest stop first
        global_stop_id = closest_stop.get("global_stop_id", None) # Get the global_stop_id of the closest stop
        # print(stops)  # Debug
        # print("Closest Stop:", closest_stop) # Debug
        # print("Global Stop ID:", global_stop_id) # Debug
        return closest_stop, global_stop_id  # Return both values
    return None, None  # Return None if request fails

#######################################################################################################################

# latitude, longitude = 41.53893285402787, -72.80120743546017 #debug - meriden station commuter parking
# Gets the routes serving a bus stop.
def get_routes_at_stop(lat, lon, max_distance=1500):
    url = "https://external.transitapp.com/v3/public/nearby_routes"
    headers = { "apiKey": API_KEY   } # API needs the key to be in the header.
    params = {  "lat": lat,
                "lon": lon,
                "max_distance": max_distance,
                "should_update_realtime": True  } # only needs lat and lon to work.
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        sentIt = response.json().get("routes", [])
        # print(f"yeet:\n{sentIt}")
        return sentIt
    else: return []
    #return response.json().get("routes", []) if response.status_code == 200 else [] # if 200, API works. else it didn't
    # I turned that one single line into that mess above just to be able to print the json response.

# display routes at stop.
def display_routes_at_stop(): # loops for days.
    user_location = entry.get()
    coordinates = get_coordinates(user_location)
    # if not coordinates: label_result.config(text="Location not found."); return
    latitude, longitude = coordinates
    """
    latitude, longitude = get_coordinates(user_location) #simple
    """
    closest_stop, global_stop_id = get_nearest_bus_stop(latitude, longitude)  # Unpack correctly
    if not closest_stop:
        label_result.config(text="No nearby bus stop found.")
        return
    routes = get_routes_at_stop(latitude, longitude, max_distance=1500)
    print("For Stop - Meriden Union Station:") # hard code this to be the var.
    for route in routes:
        strRouteShortName = route.get("route_short_name", "Unknown")
        nextDeparture = None
        for itinerary in route.get("itineraries", []):
            for schedule in itinerary.get("schedule_items", []):
                timestamp = schedule["departure_time"]
                if nextDeparture is None or timestamp < nextDeparture: nextDeparture = timestamp
        if nextDeparture:  # Convert UTC to EST (-5 hours)
            est_time = datetime.fromtimestamp(nextDeparture, UTC) - timedelta(hours=4)
            formatted_time = est_time.strftime('%I:%M %p')  # 12-hour format with AM/PM
            formatted_date = est_time.strftime('%B %d')  # %B is the datetime variable for %m written out.
            print(f"{formatted_date} Route {strRouteShortName}, Next Departure Time - {formatted_time}")
            return formatted_date, formatted_time, strRouteShortName
        return None, None, None


# display_routes_at_stop()
#######################################################################################################################

#Fetch upcoming departures for a stop.
def get_next_departure(global_stop_id):
    if not global_stop_id:
        return None
    url = "https://external.transitapp.com/v3/public/stop_departures"
    headers = {"apiKey": API_KEY}
    params = {"global_stop_id": global_stop_id, "should_update_realtime": True}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        departures = response.json().get("departures", [])
        print(departures) #Debug
        return departures[0] if departures else None
    return None

#######################################################################################################################

def search_location():
    """Handle user input, find the nearest bus stop, and update UI."""
    user_location = entry.get()
    coordinates = get_coordinates(user_location)
    if not coordinates:
        label_result.config(text="Location not found.")
        return
    latitude, longitude = coordinates
    closest_stop, global_stop_id = get_nearest_bus_stop(latitude, longitude)  # Unpack correctly
    if not closest_stop:
        label_result.config(text="No nearby bus stop found.")
        return

    stop_lat, stop_lon, stop_name = closest_stop["stop_lat"], closest_stop["stop_lon"], closest_stop["stop_name"]
    label_result.config(text=f"Nearest Bus Stop: {stop_name}")

    # Update map
    map_widget.set_position((latitude + stop_lat) / 2, (longitude + stop_lon) / 2)
    map_widget.set_zoom(15)
    map_widget.set_marker(latitude, longitude, text="Your Location")
    map_widget.set_marker(stop_lat, stop_lon, text=f"Bus Stop: {stop_name}")

    # Fetch and display routes
    # routes = get_routes_at_stop(latitude, longitude)
    # print(routes)
    display_routes_at_stop()

    # Fetch and display next departure
    next_departure = get_next_departure(global_stop_id)
    print(next_departure)

    if next_departure:
        route_name = next_departure["route_short_name"]
        arrival_time = datetime.fromtimestamp(next_departure["departure_time"], tz=timezone.utc)
        # countdown_timer(arrival_time)
        label_next_bus.config(text=f"Next Bus: {route_name} at {arrival_time.strftime('%H:%M UTC')}")
    else:
        label_next_bus.config(text="No upcoming buses.")

#######################################################################################################################

"""
def countdown_timer(arrival_time):
    # Display countdown to next bus arrival.

    def update_timer():
        while True:
            remaining = arrival_time - datetime.now(timezone.utc)
            if remaining.total_seconds() <= 0:
                countdown_var.set("Arriving Now")
                break
            countdown_var.set(str(remaining).split('.')[0])  # Format HH:MM:SS
            root.update()

    threading.Thread(target=update_timer, daemon=True).start()
"""

######################################################################################################################


tk.Label(root, text="Enter a location (meriden station commuter parking):", fg="white", bg="#1E1E1E").pack(pady=5)
entry = Entry(root, width=40)
entry.pack(pady=5)
search_button = Button(root, text="Search", command=search_location, bg="#444", fg="white")
search_button.pack(pady=5)
label_result = Label(root, text="", fg="cyan", bg="#1E1E1E")
label_result.pack(pady=5)
label_next_bus = Label(root, text="", fg="yellow", bg="#1E1E1E")
label_next_bus.pack(pady=5)
"""
countdown_var = StringVar()
countdown_var.set("--:--:--")
countdown_label = Label(root, textvariable=countdown_var, fg="red", bg="#1E1E1E", font=("Arial", 14))
countdown_label.pack(pady=5)
"""
map_widget = TkinterMapView(root, width=700, height=500)
map_widget.pack(fill="both", expand=True)
map_widget.set_position(41.6, -72.7)
map_widget.set_zoom(10)

root.mainloop()

#gui_window()

"""
#could add error handing to API get...
try:
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    json_data = response.json()
except requests.exceptions.RequestException as e:
    print(f"API request failed: {e}")
    return None
except ValueError as e:
    print(f"Error decoding JSON response: {e}")
    return None
"""
