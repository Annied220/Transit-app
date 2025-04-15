# Group 3 Project
# Transit API - Closest Stop (Details)

"""
This code gets coordinates from an address and fetches nearby bus stops from the Transit App API.
"""

##################################################   Libraries   ##################################################
import requests  # makes HTTP requests for API use
from geopy.geocoders import Nominatim  # get location details from coordinates
from geopy.distance import geodesic  # used to calculate distance between two locations.
import tkinter as tk  # creates GUI
from tkinter import messagebox, ttk  # allows the use of the messagebox; ttk is used for improved widgets.
from tkintermapview import TkinterMapView  # used for the map.
from PIL import Image, ImageTk  # image processing with pillow.
from datetime import datetime, timezone, UTC, timedelta

#################################################     API.TXT     #################################################
def api_key():
    """Reads the API key from a file named 'API.txt'."""
    try:
        with open("API.txt", "r") as file:
            API_KEY = file.read().strip()  # reads file and strips spaces.
            if not API_KEY:
                raise ValueError("API key is empty.")
            return API_KEY
    except (FileNotFoundError, ValueError) as e:
        print(f"[API Key Error] {e}")
        exit()

def max_distance():
    """Returns the maximum distance (in meters) to search for bus stops."""
    return 1000

##################################################     GeoPy     ##################################################
def get_coordinates(place):
    """Uses geopy to get latitude and longitude coordinates for a given place name."""
    try:
        geolocator = Nominatim(user_agent="GetLoc")
        location = geolocator.geocode(place,
                                      country_codes="us",  # Restrict search to the US
                                      viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)],
                                      bounded=True)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"[Geolocation Error] {e}")
    return None

#############################################     NEARBY STOP - API     #############################################
def get_nearby_bus_stops(lat, lon, stop_filter="Routable", pickup_dropoff_filter="Everything"):
    """Sends GET request to the Transit API to fetch nearby bus stops."""
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": api_key()}
    params = {
        "lat": lat,
        "lon": lon,
        "max_distance": max_distance(),
        "stop_filter": stop_filter,
        "pickup_dropoff_filter": pickup_dropoff_filter
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            stops = data.get("stops", [])
            if not stops:
                return None
            closest_stop = min(stops, key=lambda stop: stop.get("distance", float("inf")))
            return (closest_stop.get("stop_lat"),
                    closest_stop.get("stop_lon"),
                    closest_stop.get("stop_name"))
        else:
            return f"[Transit API Error] Status code: {response.status_code}"
    except Exception as e:
        return f"[API Request Error] {e}"
    return None

############################################     ROUTES AT STOP - API     ############################################
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
    return []

############################################     DISTANCE CALCULATION     ############################################
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the distance between two locations."""
    loc1 = (lat1, lon1)
    loc2 = (lat2, lon2)
    meters = geodesic(loc1, loc2).meters
    feet = meters * 3.28084
    return meters, feet

#################################################     THE GUI     #################################################
class BusStopApp:
    def __init__(self):
        # Main window parameters
        self.root = tk.Tk()
        self.root.title("Group Three  -  Nearby Bus Stop Info  -  Powered by Transit App")
        self.root.configure(bg="#1E1E1E")
        self.root.resizable(width=False, height=False)

        # Configure ttk style for the dropdown (OptionMenu)
        style = ttk.Style()
        style.theme_use('clam')  # Using a theme that supports modification
        style.configure('TMenubutton', background='darkgray', foreground='white', font=("Verdana", 12))

        monitor_height = self.root.winfo_screenheight()
        monitor_width = self.root.winfo_screenwidth()
        scale = 0.70  # 70% for window scale sizing
        window_height =  int(monitor_height * scale)
        window_width =  int(monitor_width * scale)
        y_move = 3  # vertical positioning offset
        x_move = 2  # horizontal positioning offset
        yyy = (monitor_height / y_move) - (window_height / y_move)
        xxx = (monitor_width / x_move) - (window_width / x_move)
        self.root.geometry("%dx%d+%d+%d" % (window_width, window_height, xxx, yyy))

        # Load the image for window logo
        # We may need to replace .png and/or add .ico file for the windows taskbar on compile
        imageTransitAppIcon = Image.open("Transit_App_icon.png")
        set_logo = ImageTk.PhotoImage(imageTransitAppIcon)
        self.root.iconphoto(False, set_logo)

        # Creates the window grid for GUI parts.
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)

        # Updated fonts: using Verdana for all text. Larger font (size 14) is used for stop info, distance, departures, and timer.
        standardized_font = ("Verdana", 14)

        # Search field GUI location - modified to have a gray background with a white outline.
        self.entry = tk.Entry(self.root,
                              width=42,
                              font=("Verdana", 12),
                              bg="gray",
                              fg="white",
                              insertbackground="white",
                              highlightthickness=1,
                              highlightbackground="white",
                              highlightcolor="white")
        self.entry.grid(row=0, column=2, sticky="nw", ipady=4, padx=20, pady=(19, 0))
        self.entry.bind("<Return>", lambda event: self.search_location())

        # Search button GUI location (unchanged from functionality)
        self.search_button = tk.Button(self.root,
                                       text="Search",
                                       bg='gray25',
                                       fg='white',
                                       font='Verdana',
                                       width=10,
                                       command=self.search_location)
        self.search_button.grid(row=0, column=2, sticky="ne", padx=10, pady=(20, 0))

        # Result Labels GUI location - fonts now use Verdana and font size 14, with white text.
        self.label_result = tk.Label(self.root,
                                     font=standardized_font,
                                     text="",
                                     fg="white",
                                     bg="#1E1E1E")
        self.label_result.grid(row=1, column=2, sticky="new", padx=5, pady=(2, 0))

        # For reference, this is the "second" label row which sets to this hint on launch
        self.label_distance = tk.Label(self.root,
                                       font=standardized_font,
                                       text="\U0001F50D Search up a location in CT...",
                                       fg="white",
                                       bg="#1E1E1E")
        self.label_distance.grid(row=2, column=2, sticky="new", padx=5, pady=(0, 2))

        # For reference, this is the "third" label row which sets to this hint on launch
        self.label_next_bus = tk.Label(self.root,
                                       font=standardized_font,
                                       text="\U0001F642 And we'll find your bus stop!",
                                       fg="white",
                                       bg="#1E1E1E")
        self.label_next_bus.grid(row=3, column=2, sticky="new")

        self.label_timer = tk.Label(self.root,
                                    font=standardized_font,
                                    text="",
                                    fg="white",
                                    bg="#1E1E1E")
        self.label_timer.grid(row=4, column=2, sticky="new", padx=5, pady=(2, 0))

        # Message box "View All Departures" button (left unchanged)
        self.view_all_button = tk.Button(self.root,
                                         text="View All Departures",
                                         bg='gray25',
                                         fg='white',
                                         font='Verdana',
                                         command=self.show_all_departures)
        self.view_all_button.grid(row=5, column=2, sticky="se", pady=20, padx=10)

        # Map view configuration
        self.map = TkinterMapView(self.root)
        self.map.grid(row=0, column=0, rowspan=6, columnspan=2, sticky="nsew")
        self.map.set_position(41.6, -72.7)
        self.map.set_zoom(10)

        # Track current markers
        self.user_marker = None
        self.bus_marker = None

        # Store last departure time
        self.next_departure_unix = None
        self.all_departures = ""

        # Dropdown map list (styled via the ttk style configured above)
        self.tile_server_options = {
            "OpenStreetMap ": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "OpenStreetMap": "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
            "Memo Maps": "https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png",
            "Google Maps - Roadmap": "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            "Google Maps - Hybrid": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            "Google Maps - Satellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        }
        options = list(self.tile_server_options.keys())
        selected_option = tk.StringVar(value=options[0])
        self.dropdown = ttk.OptionMenu(self.root, selected_option, *options, command=self.change_tile_server)
        self.dropdown.grid(row=5, column=2, sticky="sw", pady=19, padx=25)
        self.change_tile_server(options[0])

    # Zoom(?) tweak in case of these map selections in the dropdown
    def change_tile_server(self, selection):
        max_zoom_needed = 22 if "Google" in selection or "Memo" in selection else None
        tile_url = self.tile_server_options.get(selection)
        if tile_url:
            if max_zoom_needed:
                self.map.set_tile_server(tile_url, max_zoom=max_zoom_needed)
            else:
                self.map.set_tile_server(tile_url)

    def search_location(self):
        """Clear previous labels and markers when the search button is pressed, then set new values."""
        self.label_result.config(text="")
        self.label_distance.config(text="Distance")
        self.label_next_bus.config(text="Next Three Departures:")
        self.label_timer.config(text="")
        if self.user_marker:
            self.map.delete(self.user_marker)
            self.user_marker = None
        if self.bus_marker:
            self.map.delete(self.bus_marker)
            self.bus_marker = None

        # Tell the user when a location isn't typed in
        location = self.entry.get().strip()
        if not location:
            messagebox.showwarning("Missing Input", "Please enter a location.")
            return

        # More issue detection when we can't get the coordinates
        coords = get_coordinates(location)
        if not coords:
            self.label_result.config(text="Invalid location. Try again.")
            return

        user_lat, user_lon = coords
        self.map.set_position(user_lat, user_lon)
        if self.user_marker:
            self.map.delete(self.user_marker)
        self.user_marker = self.map.set_marker(user_lat, user_lon, text="Your Location")

        stop_info = get_nearby_bus_stops(user_lat, user_lon)
        # If no val, resolve to there being no nearby bus stops
        if not stop_info:
            self.label_result.config(text="No nearby bus stops found.")
            return

        stop_lat, stop_lon, stop_name = stop_info
        # Handles stop location specifically
        if self.bus_marker:
            self.map.delete(self.bus_marker)
        self.bus_marker = self.map.set_marker(stop_lat, stop_lon, text=f"   Stop Location: \n {stop_name}")
        self.label_result.config(text=f"Nearest Bus Stop: \n {stop_name}")

        # Set stop positioning
        distance_meters, distance_feet = calculate_distance(user_lat, user_lon, stop_lat, stop_lon)
        self.label_distance.config(text=f" {distance_meters:.2f} m \n {distance_feet:.2f} ft")
        mid_lat = (user_lat + stop_lat) / 2
        mid_lon = (user_lon + stop_lon) / 2
        self.map.set_position(mid_lat, mid_lon)

        if distance_meters < 50:
            zoom_level = 20
        elif distance_meters < 100:
            zoom_level = 19
        elif distance_meters < 200:
            zoom_level = 18
        elif distance_meters < 500:
            zoom_level = 17
        elif distance_meters < 1000:
            zoom_level = 16
        elif distance_meters < 2000:
            zoom_level = 15
        else:
            zoom_level = 14
        self.map.set_zoom(zoom_level)

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
        self.update_timer()

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
                self.label_timer.config(text="\u2705 Arriving Now!")
            else:
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                hours, mins = divmod(mins, 60)
                self.label_timer.config(text=f"\u23F0 Bus arriving in: {hours:02}:{mins:02}:{secs:02}")
                self.label_timer.after(1000, countdown)
        countdown()

    def show_all_departures(self):
        if self.all_departures:
            messagebox.showinfo("All Departures", self.all_departures)
        else:
            messagebox.showinfo("All Departures", "No departure data available.")

if __name__ == "__main__":
    app = BusStopApp()
    tk.mainloop()