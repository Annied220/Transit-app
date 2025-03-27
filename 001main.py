import requests
from geopy.geocoders import Nominatim
import tkinter as tk  # Tkinter for GUI window
from tkinter import Entry, Button, Label, StringVar
from tkintermapview import TkinterMapView
import threading
from datetime import datetime, timezone, timedelta, UTC
from pytz import timezone

# Read API key from file with error handling
try:
    with open("API.txt", "r") as file:
        API_KEY = file.read().strip()
        if not API_KEY: raise ValueError("API key is empty")
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
    exit()

DEFAULT_MAX_DISTANCE = 1500


# Get latitude and longitude from user-specified address
def get_coordinates(place):
    geolocator = Nominatim(user_agent="GetLoc")
    try:
        location = geolocator.geocode(
            place, country_codes="us", viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)], bounded=True
        )
        return (location.latitude, location.longitude) if location else None
    except Exception as e:
        print(f"Error with geocoding: {e}")
        return None


# Get nearest bus stop based on location
def get_nearest_bus_stop(lat, lon, max_distance=DEFAULT_MAX_DISTANCE):
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": API_KEY}
    params = {"lat": lat, "lon": lon, "max_distance": max_distance}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        stops = response.json().get("stops", [])
        if not stops:
            return None, None  # No stops found
        closest_stop = min(stops, key=lambda stop: stop['distance'])
        global_stop_id = closest_stop.get("global_stop_id", None)
        return closest_stop, global_stop_id
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching bus stops: {e}")
        return None, None


# Get available routes for a bus stop
def get_routes_at_stop(lat, lon, max_distance=DEFAULT_MAX_DISTANCE):
    url = "https://external.transitapp.com/v3/public/nearby_routes"
    headers = {"apiKey": API_KEY}
    params = {"lat": lat, "lon": lon, "max_distance": max_distance, "should_update_realtime": True}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("routes", [])
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching routes: {e}")
        return []


# Fetch next departure time for a bus stop
def get_next_departure(global_stop_id):
    url = "https://external.transitapp.com/v3/public/stop_departures"
    headers = {"apiKey": API_KEY}
    params = {"global_stop_id": global_stop_id, "should_update_realtime": True}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        departures = response.json().get("departures", [])
        return departures[0] if departures else None
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching next departures: {e}")
        return None


# Convert timestamp to local time (EST)
def convert_to_local_time(timestamp):
    try:
        utc_time = datetime.fromtimestamp(timestamp, UTC)
        local_time = utc_time.astimezone(timezone("US/Eastern"))
        return local_time.strftime("%I:%M %p"), local_time.strftime("%B %d")
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return None, None


# Search location and update display
def search_location():
    user_location = entry.get().strip()
    if not user_location:
        label_result.config(text="Please enter a valid location.")
        return

    coordinates = get_coordinates(user_location)
    if not coordinates:
        label_result.config(text="Location not found.")
        return

    latitude, longitude = coordinates
    closest_stop, global_stop_id = get_nearest_bus_stop(latitude, longitude)
    if not closest_stop:
        label_result.config(text="No nearby bus stop found.")
        return

    stop_lat, stop_lon, stop_name = closest_stop["stop_lat"], closest_stop["stop_lon"], closest_stop["stop_name"]
    label_result.config(text=f"Nearest Bus Stop: {stop_name}")

    # Update map widget
    map_widget.set_position((latitude + stop_lat) / 2, (longitude + stop_lon) / 2)
    map_widget.set_zoom(15)
    map_widget.set_marker(latitude, longitude, text="Your Location")
    map_widget.set_marker(stop_lat, stop_lon, text=f"Bus Stop: {stop_name}")

    # Fetch next departure
    next_departure = get_next_departure(global_stop_id)
    if next_departure:
        departure_time, departure_date = convert_to_local_time(next_departure["departure_time"])
        if departure_time and departure_date:
            label_next_bus.config(
                text=f"Next Bus: {next_departure['route_short_name']} on {departure_date} at {departure_time}")
            countdown_timer(datetime.fromtimestamp(next_departure["departure_time"], UTC))
        else:
            label_next_bus.config(text="Error with next bus information.")
    else:
        label_next_bus.config(text="No upcoming buses.")


def countdown_timer(arrival_time):
    def update_timer():
        while True:
            remaining = arrival_time - datetime.now(timezone.utc)
            if remaining.total_seconds() <= 0:
                countdown_var.set("Arriving Now")
                break
            countdown_var.set(str(remaining).split('.')[0])  # Format HH:MM:SS
            root.after(1000, update_timer)  # Schedule updates
            break

    threading.Thread(target=update_timer, daemon=True).start()


# Initialize Tkinter Window
root = tk.Tk()
root.title("Bus Stop Finder")
root.geometry("700x600")
root.configure(bg="#1E1E1E")  # Dark Mode Background

tk.Label(root, text="Enter a location:", fg="white", bg="#1E1E1E").pack(pady=5)
entry = Entry(root, width=40)
entry.pack(pady=5)
search_button = Button(root, text="Search", command=search_location, bg="#444", fg="white")
search_button.pack(pady=5)
label_result = Label(root, text="", fg="cyan", bg="#1E1E1E")
label_result.pack(pady=5)
label_next_bus = Label(root, text="", fg="yellow", bg="#1E1E1E")
label_next_bus.pack(pady=5)
countdown_var = StringVar()
countdown_var.set("--:--:--")
countdown_label = Label(root, textvariable=countdown_var, fg="red", bg="#1E1E1E", font=("Arial", 14))
countdown_label.pack(pady=5)

# Initialize map widget
map_widget = TkinterMapView(root, width=600, height=400)
map_widget.pack(pady=10)
map_widget.set_zoom(10)

root.mainloop()
