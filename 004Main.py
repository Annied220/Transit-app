from geopy.geocoders import Nominatim
import requests
import tkinter as tk
from tkinter import Entry, Button, Label, StringVar
from tkintermapview import TkinterMapView
import threading
from datetime import datetime, timezone, timedelta

try:
    with open("API.txt", "r") as file:
        API_KEY = file.read()
        if not API_KEY: raise ValueError("API key is empty")
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
    exit()

# Get latitude and longitude from user input address
def get_coordinates(place):
    geolocator = Nominatim(user_agent="GetLoc")
    location = geolocator.geocode(
        place, country_codes="us", viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)], bounded=True
    )
    return (location.latitude, location.longitude) if location else None

# Get nearest bus stop
def get_nearest_bus_stop(lat, lon, max_distance=1000):
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": API_KEY}
    params = {"lat": lat, "lon": lon, "max_distance": max_distance}
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        stops = response.json().get("stops", [])
        if not stops:
            return None, None
        closest_stop = min(stops, key=lambda stop: stop['distance'])
        global_stop_id = closest_stop.get("global_stop_id", None)
        return closest_stop, global_stop_id
    return None, None

# Fetch routes serving a stop
def get_routes_at_stop(lat, lon, max_distance=1500):
    url = "https://external.transitapp.com/v3/public/nearby_routes"
    headers = {"apiKey": API_KEY}
    params = {"lat": lat, "lon": lon, "max_distance": max_distance, "should_update_realtime": True}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("routes", []) if response.status_code == 200 else []

# Fetch upcoming departures
def get_next_departure(global_stop_id):
    if not global_stop_id:
        return None
    url = "https://external.transitapp.com/v3/public/stop_departures"
    headers = {"apiKey": API_KEY}
    params = {"global_stop_id": global_stop_id, "should_update_realtime": True}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        departures = response.json().get("departures", [])
        return departures[0] if departures else None
    return None

# Search and update UI
def search_location():
    user_location = entry.get()
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

    map_widget.set_position((latitude + stop_lat) / 2, (longitude + stop_lon) / 2)
    map_widget.set_zoom(15)
    map_widget.set_marker(latitude, longitude, text="Your Location")
    map_widget.set_marker(stop_lat, stop_lon, text=f"Bus Stop: {stop_name}")

    routes = get_routes_at_stop(latitude, longitude)
    route_info = []
    for route in routes:
        route_name = route.get("route_short_name", "Unknown")
        next_departure = None
        if global_stop_id:
            departure = get_next_departure(global_stop_id)
            if departure:
                next_departure = datetime.fromtimestamp(departure["departure_time"], tz=timezone.utc) - timedelta(hours=4)
                countdown_timer(next_departure)
                formatted_time = next_departure.strftime('%I:%M %p')
                countdown_text = str(next_departure - datetime.now(timezone.utc)).split('.')[0]
                route_info.append(f"Route {route_name} - {formatted_time} - {countdown_text}")
            else:
                route_info.append(f"Route {route_name} - No upcoming departure")
    label_routes.config(text=f"Routes Available:\n" + "\n".join(route_info))

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

# Initialize UI
root = tk.Tk()
root.title("Bus Stop Finder")
root.geometry("700x600")
root.configure(bg="#1E1E1E")

Label(root, text="Enter a location:", fg="white", bg="#1E1E1E").pack(pady=5)
entry = Entry(root, width=40)
entry.pack(pady=5)
Button(root, text="Search", command=search_location, bg="#444", fg="white").pack(pady=5)
label_result = Label(root, text="", fg="cyan", bg="#1E1E1E")
label_result.pack(pady=5)
label_routes = Label(root, text="", fg="lightblue", bg="#1E1E1E")
label_routes.pack(pady=5)
label_next_bus = Label(root, text="", fg="yellow", bg="#1E1E1E")
label_next_bus.pack(pady=5)

countdown_var = StringVar()
countdown_var.set("--:--:--")
Label(root, textvariable=countdown_var, fg="red", bg="#1E1E1E", font=("Arial", 14)).pack(pady=5)

map_widget = TkinterMapView(root, width=700, height=500)
map_widget.pack(fill="both", expand=True)
map_widget.set_position(41.6, -72.7)
map_widget.set_zoom(10)

root.mainloop()
