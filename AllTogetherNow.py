# want to add a function that outputs the difference in meters (and feet) from one stop to the other.

import requests
import threading

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

import tkinter as tk
from tkinter import messagebox

from gmpy2 import RoundUp
from tkintermapview import TkinterMapView
from PIL import Image, ImageTk

import time
from datetime import datetime, timezone, UTC, timedelta

# Get the current UTC time (timezone-aware)
utc_now = datetime.now(timezone.utc)


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
    return 1000  # max = 1500


# we could attach this variable to a sliding bar,
# that sliding bar could change the size of a circle in the GUI map to show radius
# this is an unnecessary addition to the scope - but might be fun

# tries to call geopy
def get_coordinates(place):
    """Uses geopy to get latitude and longitude coordinates for a given place name."""
    try:
        geolocator = Nominatim(user_agent="GetLoc")  # https://www.youtube.com/watch?v=mhTkaH2YuAc
        location = geolocator.geocode(place,
                                      country_codes="us",  # Restrict search to the US
                                      viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)],
                                      # Bounding box for Connecticut
                                      bounded=True  # Ensures results stay within the view box
                                      )  # everything here is learned from the documentation
                                         # https://geocoder.readthedocs.io/results.html
        if location:
            # print((location.latitude, location.longitude)) # Debugging. Outputs Lat and Lon.
            # print(location.raw) # Debugging. # full data pull
            return location.latitude, location.longitude  #THIS SHOULD BE REFERENCED BY TK AS "Your Location"
    except Exception as e:
        print(f"[Geolocation Error] {e}")
    return None  # outputs nothing


#
def get_nearby_bus_stops(lat, lon, stop_filter="Routable", pickup_dropoff_filter="Everything"):
    """Sends GET request to the Transit API to fetch nearby bus stops."""
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": api_key()}  # Headers for the request
    params = {  # Parameters to be sent in the API request
        "lat": lat,  # Latitude of the location. REQUIRED
        "lon": lon,  # Longitude of the location. REQUIRED
        "max_distance": max_distance(),
        "stop_filter": stop_filter,
        "pickup_dropoff_filter": pickup_dropoff_filter
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:  # 200 code is a successful call per their API docs
            data = response.json()
            # print(data)  #debugging
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
            ) #THIS SHOULD BE REFERENCED BY TK AS A POINT ON THE MAP "Closest Stop: stop_name"
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
    return []  # returns json response list


# user input applied to
def closest_stop_to_input():
    """Gets user input, geocodes it, and returns the closest bus stop's coordinates."""
    while True:
        strUserInputLocation = input("Enter a location (or press Enter to exit): ").strip()
        if not strUserInputLocation:
            invalid_entry_message = "Invalid Entry. Try again."
            print(invalid_entry_message)
            # return invalid_entry_message
            continue
        """ might not work in the GUI """

        coordinates = get_coordinates(strUserInputLocation)
        if coordinates:
            lat, lon = coordinates
            # print(f"Location: {strUserInputLocation} ({lat}, {lon})") # debug
            closest_stop = get_nearby_bus_stops(lat, lon)
            if closest_stop:
                stop_lat, stop_lon, stop_name = closest_stop
                print(
                    f"Closest Bus Stop: {stop_name} ({stop_lat}, {stop_lon})")
                return stop_lat, stop_lon
            else:
                print("Could not find any nearby bus stops.")
                no_stops_message = "Could not find any nearby bus stops."
                return no_stops_message
        else:
            print("Invalid location. Please try again.")
            invalid_location_message = "Invalid location. Please try again."
            return invalid_location_message

def calculate_distance(lat1, lon1, lat2, lon2):
    loc1 = (lat1, lon1)
    loc2 = (lat2, lon2)
    meters = geodesic(loc1, loc2).meters
    feet = meters * 3.28084
    return meters, feet

class BusStopApp:
    def __init__(self):
        # main window parameters
        self.root = tk.Tk()
        self.root.title("Group Three  -  Nearby Bus Stop Info  -  Powered by Transit App")
        self.root.geometry("800x400")
        self.root.configure(bg="#1E1E1E")
        self.root.eval("tk::PlaceWindow . center")
        # Disable window resizing
        self.root.resizable(width=False, height=False)

        # Load the image for window logo
        imageTransitAppIcon = Image.open("Transit_App_icon.png")
        set_logo = ImageTk.PhotoImage(imageTransitAppIcon)
        # Set the icon
        self.root.iconphoto(False, set_logo)


        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)

        # Search field
        self.entry = tk.Entry(self.root, width=30)
        self.entry.grid(row=0, column=1, sticky="nw", padx=20, pady=(23, 0))
        self.entry.bind("<Return>", lambda event: self.search_location())

        self.search_button = tk.Button(self.root, text="Search", width=11, command=self.search_location)
        self.search_button.grid(row=0, column=1, sticky="ne", padx=20, pady=(20, 0))


        # Result Labels
        self.label_result = tk.Label(self.root, text="Stop Information...", fg="cyan", bg="#1E1E1E")
        self.label_result.grid(row=1, column=1, sticky="nsew", padx=5, pady=(5, 0))

        self.label_distance = tk.Label(self.root, text="Distance", fg="lightblue", bg="#1E1E1E")
        self.label_distance.grid(row=2, column=1, sticky="nsew", padx=5, pady=(0, 5))

        self.label_next_bus = tk.Label(self.root, text="Next Three Departures:", fg="yellow", bg="#1E1E1E")
        self.label_next_bus.grid(row=3, column=1, sticky="nsew", padx=5, pady=(5, 0))

        self.label_timer = tk.Label(self.root, text="00:00:00", fg="lightgreen", bg="#1E1E1E")
        self.label_timer.grid(row=4, column=1, sticky="nsew", padx=5, pady=(5, 0))

        self.view_all_button = tk.Button(self.root, text="View All Departures", command=self.show_all_departures)
        self.view_all_button.grid(row=5, column=1, sticky="se", pady=20, padx=20)

        # Map view
        self.map = TkinterMapView(self.root)
        self.map.grid(row=0, column=0, rowspan=6, sticky="nsew")
        self.map.set_position(41.6, -72.7)
        self.map.set_zoom(10)

        # Track current markers
        self.user_marker = None
        self.bus_marker = None

        # Store last departure time
        self.next_departure_unix = None
        self.all_departures = ""

        self.tile_server_options = {
            "OpenStreetMap": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Memo Maps": "https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
            "Google Maps (Roadmap)": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            "Google Maps (Hybrid)": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            "Google Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        }

        options = list(self.tile_server_options.keys())
        selected_option = tk.StringVar(value=options[0])
        self.dropdown = tk.OptionMenu(self.root, selected_option, *options, command=self.change_tile_server)
        self.dropdown.grid(row=5, column=1, sticky="sw", pady=20, padx=20)

        self.change_tile_server(options[0])

    def change_tile_server(self, selection):
        max_zoom_needed = 22 if "Google" in selection or "Memo" in selection else None
        tile_url = self.tile_server_options.get(selection)
        if tile_url:
            if max_zoom_needed:
                self.map.set_tile_server(tile_url, max_zoom=max_zoom_needed)
            else:
                self.map.set_tile_server(tile_url)

    def search_location(self):

        # Clear previous labels and markers
        self.label_result.config(text="")  # Clear the result label
        self.label_distance.config(text="Distance")  # Clear the result label
        self.label_next_bus.config(text="Next Three Departures:")  # Clear the next bus label
        self.label_timer.config(text="")  # Clear the timer label
        if self.user_marker:
            self.map.delete(self.user_marker)  # Remove previous user marker
            self.user_marker = None
        if self.bus_marker:
            self.map.delete(self.bus_marker)  # Remove previous bus stop marker
            self.bus_marker = None

        location = self.entry.get().strip()
        if not location:
            messagebox.showwarning("Missing Input", "Please enter a location.")
            return

        coords = get_coordinates(location)
        if not coords:
            self.label_result.config(text="Invalid location. Try again.")
            return

        user_lat, user_lon = coords
        self.map.set_position(user_lat, user_lon)
        if self.user_marker:
            self.map.delete(self.user_marker)
        self.user_marker = self.map.set_marker(user_lat, user_lon, text=f"Your Location")

        stop_info = get_nearby_bus_stops(user_lat, user_lon)
        if not stop_info:
            self.label_result.config(text="No nearby bus stops found.")
            return

        stop_lat, stop_lon, stop_name = stop_info
        if self.bus_marker:
            self.map.delete(self.bus_marker)
        self.bus_marker = self.map.set_marker(stop_lat, stop_lon, text=f"   Stop Location: \n {stop_name}")

        self.label_result.config(text=f"Nearest Bus Stop: {stop_name}")

        distance_meters, distance_feet = calculate_distance(user_lat,user_lon, stop_lat, stop_lon)

        self.label_distance.config(text=f" {distance_meters:.2f} m \n {distance_feet:.2f} ft")

        self.map.set_position((user_lat + stop_lat) / 2, (user_lon + stop_lon) / 2)
        self.map.set_zoom(16) # (RoundUp(distance_meters/10)) ########################################################################################################

        routes = get_routes_at_stop(stop_lat, stop_lon)
        if not routes:
            self.label_next_bus.config(text="No routes found.")
            return

        upcoming_routes = []
        for route in routes:
            route_short_name = route.get("route_short_name", "Unknown")
            next_time = None
            for itinerary in route.get("itineraries", []):
                for schedule in itinerary.get("schedule_items", []):
                    ts = schedule.get("departure_time")
                    if ts and (next_time is None or ts < next_time):
                        next_time = ts
            if next_time:
                upcoming_routes.append({
                    "route": route_short_name,
                    "departure_time": next_time
                })

        if not upcoming_routes:
            self.label_next_bus.config(text="No departures found.")
            return

        upcoming_routes.sort(key=lambda r: r["departure_time"])
        self.next_departure_unix = upcoming_routes[0]["departure_time"]
        self.update_timer()  # start countdown

        msg_3 = ""
        self.all_departures = ""
        for i, route_info in enumerate(upcoming_routes[:-1]):
            est_time = datetime.fromtimestamp(route_info["departure_time"], UTC) - timedelta(hours=4)
            formatted_time = est_time.strftime('%I:%M %p')
            formatted_date = est_time.strftime('%B %d')
            line = f"{formatted_date} | Route {route_info['route']} | Next Departure: {formatted_time}"
            if i < 3:
                msg_3 += line + "\n"
            self.all_departures += line + "\n"

        self.label_next_bus.config(text="Next Three Departures:\n" + msg_3)

    def update_timer(self):
        def countdown():
            if self.next_departure_unix is None:
                self.label_timer.config(text="No departure time set.")
                return

            now = datetime.now(timezone.utc)
            remaining = datetime.fromtimestamp(self.next_departure_unix, timezone.utc) - now

            if remaining.total_seconds() <= 0:
                self.label_timer.config(text="Arriving Now!")
            else:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                hours, mins = divmod(mins, 60)
                self.label_timer.config(text=f"Bus arriving in: {hours:02}:{mins:02}:{secs:02}")
                self.label_timer.after(1000, countdown)  # Call itself after 1 second

        countdown()

    def show_all_departures(self):
        if self.all_departures:
            messagebox.showinfo("All Departures", self.all_departures)
        else:
            messagebox.showinfo("All Departures", "No departure data available.")

if __name__ == "__main__":
    app = BusStopApp()
    tk.mainloop()



"""
        def change_tile_server(selection):
            tile_servers = {
                "OpenStreetMap": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "Memo Maps": "https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
                "Google Maps (Roadmap)": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
                "Google Maps (Hybrid)": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                "Google Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            }

            max_zoom_needed = 22 if "Google" in selection or "Memo" in selection else None

            if max_zoom_needed:
                self.map_widget.set_tile_server(tile_servers[selection], max_zoom=max_zoom_needed)
            else:
                self.map_widget.set_tile_server(tile_servers[selection])

        # Dropdown for tile server selection
        options = ["OpenStreetMap",
                   "Memo Maps",
                   "Google Maps (Roadmap)",
                   "Google Maps (Hybrid)",
                   "Google Satellite"]
        selected_option = tk.StringVar(value=options[0])
        self.dropdown = tk.OptionMenu(self.root, selected_option, *options, command = self.change_tile_server)
        self.dropdown.grid(row=4, column=1, sticky="sw", pady=20, padx=20)

        # Set default tile server
        change_tile_server(options[0])
"""
"""
        #self.map.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
        #self.map.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google normal
        #self.map.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite

        
        # broken
        self.map.set_tile_server("http://c.tile.stamen.com/watercolor/{z}/{x}/{y}.png")  # painting style
        self.map.set_tile_server("http://a.tile.stamen.com/toner/{z}/{x}/{y}.png")  # black and white
        self.map.set_tile_server("https://tiles.wmflabs.org/hikebike/{z}/{x}/{y}.png")  # detailed hiking
        self.map.set_tile_server("https://tiles.wmflabs.org/osm-no-labels/{z}/{x}/{y}.png")  # no labels
        self.map.set_tile_server("https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg")  # swisstopo map
        
        # example overlay tile server
        self.map.set_overlay_tile_server("http://tiles.openseamap.org/seamark//{z}/{x}/{y}.png")  # sea-map overlay
        self.map.set_overlay_tile_server("http://a.tiles.openrailwaymap.org/standard/{z}/{x}/{y}.png")  # railway infrastructure
"""

"""
def update_timer(self):
    def countdown():
        while True:
            if self.next_departure_unix is None:
                return
            remaining = datetime.fromtimestamp(self.next_departure_unix, UTC) - utc_now

            if remaining.total_seconds() <= 0:
                self.label_timer.config(text="Arriving Now!")
                break
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            hours, mins = divmod(mins, 60)
            self.label_timer.config(text=f"Bus arriving in: {hours:02}:{mins:02}:{secs:02}")
            time.sleep(1)
"""
"""
# Assuming UTC is defined as:
UTC = timezone.utc  # Ensure UTC timezone is set

def update_timer(self):
    def countdown():
        if self.next_departure_unix is None:
            self.label_timer.config(text="No departure time set.")
            return

        remaining = datetime.fromtimestamp(self.next_departure_unix, UTC) - utc_now

        if remaining.total_seconds() <= 0:
            self.label_timer.config(text="Arriving Now!")
        else:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            hours, mins = divmod(mins, 60)
            self.label_timer.config(text=f"Bus arriving in: {hours:02}:{mins:02}:{secs:02}")
            # Schedule the next countdown call after 1000 milliseconds (1 second)
            self.label_timer.after(1000, countdown)

    countdown()  # Start the countdown

    threading.Thread(target=countdown, daemon=True).start()
    """





