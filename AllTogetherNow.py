# Group 3 Project
# Transit API - Closest Stop (Details)

"""
This code gets coordinates from an address and fetches nearby bus stops from the Transit App API.
"""

# Updates:
# Resizeable window, patched all outstanding issues and visual quirks. Hopefully this build sticks it.

# Concerns:
# Application is functional and considered feature complete. Doing final pass on WEEK 14 to determine there
# are no more issues prior to presentation and will be testing the application on a school computer.

##################################################   Libraries   ##################################################

import requests # makes HTTP requests for API use # https://www.w3schools.com/python/module_requests.asp
from geopy.geocoders import Nominatim # get location details from coordinates # https://geopy.readthedocs.io/en/stable/
from geopy.distance import geodesic #used in line 175 to calc the distance between the 2 locations to get distance.
import tkinter as tk # creates GUI
from tkinter import messagebox, ttk # allows the use of the message box, tkk fixes the dropout map selector.
#from gmpy2 import RoundUp # instead of importing this, we used "int() to convert the float to an int.
from tkintermapview import TkinterMapView # used for the map.
from PIL import Image, ImageTk #pillow. python image Library (PIL) # https://pypi.org/project/pillow/
#import threading # used in past version to run all parts of a for loop at the same time.
#import time # used prior, replaced with datetime
from datetime import datetime,timezone,UTC,timedelta #https://docs.python.org/3/library/datetime.html#datetime.datetime

#other geopy info
#    https://stackoverflow.com/questions/60928516/get-address-from-given-coordinate-using-python
#    https://geopy.readthedocs.io/en/stable/#module-geopy.geocoders
#    https://github.com/DenisCarriere/geocoder/blob/master/README.md
#    https://geocoder.readthedocs.io/results.html

#################################################     API.TXT     #################################################

# tries to read API.txt. this is to prevent the API key from being hard coded into program.
def api_key():
    """Reads the API key from a file named 'API.txt'."""
    try:
        with open("API.txt", "r") as file:
            API_KEY = file.read().strip()  # reads file and strips spaces.
            if not API_KEY:
                raise ValueError("API key is empty.")
            return API_KEY
    except (FileNotFoundError, ValueError) as e:
        print(f"[API Key Error] {e}") # if there is an API error, prints issue in IDE.
        exit() # if there is an API error, closes the program.

# because there are 2 APIs that use this, make it a function.
def max_distance():
    """Returns the maximum distance (in meters) to search for bus stops."""
    return 1000 # API default is 150
# this is not required for the APIs, or our code, but it is useful to define if we were to add more functionality.

# could add a function that separates the steps, creates a circle around the users set location based on this value,
# and have it display every stop and their distance from the user. then, when they select it, it pushes the stop info.
# we could attach this variable to a sliding bar,
# that sliding bar could change the size of a circle in the GUI map to show radius
# this is an unnecessary addition to the scope - but might be fun

##################################################     GeoPy     ##################################################

# try to call geopy
def get_coordinates(place):
    """Uses geopy to get latitude and longitude coordinates for a given place name."""
    try:
        geolocator = Nominatim(user_agent="GetLoc") # https://www.youtube.com/watch?v=mhTkaH2YuAc
        location = geolocator.geocode(place,
                                      country_codes="us",  # Restrict search to the US
                                      # Bounding box for Connecticut
                                      viewbox=[(42.050587, -73.727775), (40.950943, -71.787220)],
                                      bounded=True) # Ensures results stay within the view box
        # everything here is learned from the documentation
        # https://geocoder.readthedocs.io/results.html
        if location:
            # print((location.latitude, location.longitude)) # Debugging. Outputs Lat and Lon.
            # print(location.raw) # Debugging. # full data pull
            return location.latitude, location.longitude
    except Exception as e:
        print(f"[Geolocation Error] {e}") # pushes error
    return None # outputs nothing

#############################################     NEARBY STOP - API     #############################################

# tries to call transitApp API
def get_nearby_bus_stops(lat, lon, stop_filter="Routable", pickup_dropoff_filter="Everything"):
    """Sends GET request to the Transit API to fetch nearby bus stops."""
    url = "https://external.transitapp.com/v3/public/nearby_stops"
    headers = {"apiKey": api_key()} # Headers for the request
    params = { # Parameters to be sent in the API request
        "lat": lat, # Latitude of the location. REQUIRED
        "lon": lon, # Longitude of the location. REQUIRED
        "max_distance": max_distance(), # helps limit search
        "stop_filter": stop_filter, # helps limit search
        "pickup_dropoff_filter": pickup_dropoff_filter # helps limit search
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10) #timeout times out after 10 seconds.
        if response.status_code == 200: # 200 code is a successful call per their API docs
            data = response.json() # this is the raw data from the API.
            # print(data)  #debugging
            stops = data.get("stops", []) #pulls the stop info from the json
            # Ensure "stops" key exists and is non-empty before accessing
            if not stops:
                return None #use to: print("No nearby bus stops found.") now we are on the GUI.
            closest_stop = min(stops, key=lambda stop: stop.get("distance", float("inf")))
            return (closest_stop.get("stop_lat"),
                    closest_stop.get("stop_lon"),
                    closest_stop.get("stop_name"))
        else:
            return f"[Transit API Error] Status code: {response.status_code}"
    except Exception as e:
        return f"[API Request Error] {e}"
    return None


# I do not think the about print codes are doing much of anything now that we are in the GUI.
# need to replace this with a return (same thing the print does) and have it go to one of the labels or a messagebox.


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
    """Calculates the distance between two locations/between user and stop location."""
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
        self.root.withdraw() # Hide blank GUI (screw Tkinter)
        self.root.title("Group Three  -  Nearby Bus Stop Info  -  Powered by Transit App")
        self.root.configure(bg="#1E1E1E")
        #self.root.resizable(width=False, height=False)

        # Configure ttk style for the dropdown (OptionMenu)
        style = ttk.Style()
        style.theme_use('clam')  # Using a theme that supports modification
        style.configure('TMenubutton', background='darkgray', foreground='white', font=("Verdana", 12))

        # Load the image for window logo
        # We may need to replace .png and/or add .ico file for the windows taskbar on compile
        imageTransitAppIcon = Image.open("Transit_App_icon.png")
        set_logo = ImageTk.PhotoImage(imageTransitAppIcon)
        self.root.iconphoto(False, set_logo)


        # Updated fonts: using Verdana for all text. Larger font (size 14) is used for stop info, distance, departures, and timer.
        standardized_font = ("Verdana", 14)

        #Create Frames ===
        self.top_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.middle_frame = tk.Frame(self.root, bg="#1E1E1E")
        self.bottom_frame = tk.Frame(self.root, bg="#1E1E1E")

        self.top_frame.pack(fill="x")
        self.middle_frame.pack(fill="both", expand=True)
        self.bottom_frame.pack(fill="x")

        # Search field GUI location - modified to have a gray background with a white outline.
        self.entry = tk.Entry(self.top_frame,
                              width=42,
                              font=("Verdana", 12),
                              bg="gray",
                              fg="white",
                              insertbackground="white",
                              highlightthickness=1,
                              highlightbackground="white",
                              highlightcolor="white")
        self.entry.pack(side="left", padx=10, pady=10, ipady=4)
        self.entry.bind("<Return>", lambda event: self.search_location())

        # Functions to add placeholder to the input field
        def on_entry_click(event):
            if self.entry.get() == placeholder:
                self.entry.delete(0, "end")  # delete all the text in the entry
                self.entry.config(fg='white')  # set the color to black for normal text

        def on_focusout(event):
            if self.entry.get() == '':
                self.entry.insert(0, placeholder)
                self.entry.config(fg='grey')

        placeholder = "Enter location..."
        self.entry.insert(0, placeholder)
        self.entry.bind('<FocusIn>', on_entry_click)
        self.entry.bind('<FocusOut>', on_focusout)

        # Search button GUI location (unchanged from functionality)
        self.search_button = tk.Button(self.top_frame,
                                       text="Search",
                                       bg='gray25',
                                       fg='white',
                                       font='Verdana',
                                       width=10,
                                       command=self.search_location)
        self.search_button.pack(side="left", padx=10, pady=10)

        # === Middle Frame: Map ===
        # Map view configuration
        self.map = TkinterMapView(self.middle_frame)
        self.map.pack(fill="both", expand=True, padx=10, pady=10)
        self.map.set_position(41.6, -72.7)
        self.map.set_zoom(10)

        # === Bottom Frame: Results & Buttons ===
        # Result Labels GUI location - fonts now use Verdana and font size 14, with white text.
        self.label_result = tk.Label(self.bottom_frame,
                                     font=standardized_font,
                                     text="",
                                     fg="white",
                                     bg="#1E1E1E")
        self.label_result.pack(anchor="w", padx=20)

        # For reference, this is the "second" label row which sets to this hint on launch
        self.label_distance = tk.Label(self.bottom_frame,
                                       font=standardized_font,
                                       text="\U0001F50D Search up a location in CT...",
                                       fg="white",
                                       bg="#1E1E1E")
        self.label_distance.pack(anchor="w", padx=20)

        # For reference, this is the "third" label row which sets to this hint on launch
        self.label_next_bus = tk.Label(self.bottom_frame,
                                       font=standardized_font,
                                       text="\U0001F642 And we'll find your bus stop!",
                                       fg="white",
                                       bg="#1E1E1E")
        self.label_next_bus.pack(anchor="w", padx=20)

        self.label_timer = tk.Label(self.bottom_frame,
                                    font=standardized_font,
                                    text="",
                                    fg="white",
                                    bg="#1E1E1E")
        self.label_timer.pack(anchor="w", padx=20)

        # Message box "View All Departures" button (left unchanged)
        self.view_all_button = tk.Button(self.bottom_frame,
                                         text="View All Departures",
                                         bg='gray25',
                                         fg='white',
                                         font='Verdana',
                                         command=self.show_all_departures)
        self.view_all_button.pack(side="left", padx=20, pady=10)


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
        self.dropdown = ttk.OptionMenu(self.bottom_frame, selected_option, *options, command=self.change_tile_server)
        self.dropdown.pack(side="left", padx=20, pady=10)
        self.change_tile_server(options[0])

        # Debounced resize handler
        self._resize_job = None  # was self.resize_after_id
        self.last_w, self.last_h = self.root.winfo_width(), self.root.winfo_height()
        self.current_mode = None
        self.current_state = self.root.state()  # track whether we're 'normal', 'zoomed', etc.
        self.initial_geometry = self.root.geometry()  # remember the launch size/position
        self.root.bind("<Configure>", self.on_configure)  # bind our new debounced method

        self.root.update_idletasks()  # make sure geometry info is up to date
        self.root.deiconify() # Show the window fully rendered now
        # ─── HACKY TILE-RELOAD ─────────────────────────────────────────────
        # force a re-set of the OSM tiles a moment after launch
        # selected_option is tk.StringVar for the dropdown
        self.root.after(500, lambda: self.change_tile_server(selected_option.get()))
        self.initial_geometry = self.root.geometry()  # e.g. "800x600+X+Y"
        self.current_state = self.root.state()  # e.g. "normal"

        # Config Grid Layout
        for col in range(6):
            self.root.columnconfigure(col, weight=1)  # Makes columns expand equally

        for row in range(3):
            self.root.rowconfigure(row, weight=1)  # Makes rows expand equally

    def on_configure(self, event):
        # 1) Handle maximize <-> restore
        new_state = self.root.state()
        if new_state != self.current_state:
            # if we're restoring from a maximized window…
            if self.current_state == "zoomed" and new_state == "normal":
                self.root.geometry(self.initial_geometry)
            self.current_state = new_state
        # 2) ignore drag/move without resize
        if event.width == self.last_w and event.height == self.last_h:
            return
        # record new size
        self.last_w, self.last_h = event.width, event.height

        # debounce: wait 150ms after the last resize event
        if self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(150, self.responsive_layout)

    def responsive_layout(self, event=None):
        width = self.root.winfo_width()
        mode = "mobile" if width < 600 else "desktop"
        if mode == self.current_mode:
            return  # already in the right layout, so do nothing
        self.current_mode = mode

        # Always forget previous layout before switching
        self.top_frame.pack_forget()
        self.middle_frame.pack_forget()
        self.bottom_frame.pack_forget()
        self.top_frame.grid_forget()
        self.middle_frame.grid_forget()
        self.bottom_frame.grid_forget()

        if width < 600:
            # Mobile style layout (stacked vertically)
            self.top_frame.grid(row=0, column=0, columnspan=6, sticky="nsew")
            self.middle_frame.grid(row=1, column=0, columnspan=6, sticky="nsew")
            self.bottom_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
        else:
            # === Desktop layout ===
            self.top_frame.pack_forget()
            self.middle_frame.pack_forget()
            self.bottom_frame.pack_forget()

            #Repack top_frame, middle_frame, bottom_frame
            self.middle_frame.grid(row=0, column=0, rowspan=6, columnspan=3, sticky="nsew")
            self.top_frame.grid(row=0, column=3, columnspan=3, rowspan=1, sticky="nsew")
            self.bottom_frame.grid(row=1, column=3, columnspan=3, rowspan=1, sticky="nsew")

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
        self.label_distance.config(text="Please wait...")
        self.label_next_bus.config(text="Gathering data.")
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
        # Handles map location specifically
        if self.bus_marker:
            self.map.delete(self.bus_marker)
        self.bus_marker = self.map.set_marker(stop_lat, stop_lon, text=f"   Stop Location: \n {stop_name}")
        self.label_result.config(text=f"Nearest Bus Stop: \n {stop_name}")

        # Set map positioning
        distance_meters, distance_feet = calculate_distance(user_lat, user_lon, stop_lat, stop_lon)
        self.label_distance.config(text=f" {distance_meters:.2f} m \n {distance_feet:.2f} ft")
        mid_lat = (user_lat + stop_lat) / 2
        mid_lon = (user_lon + stop_lon) / 2
        self.map.set_position(mid_lat, mid_lon)

        # Set Zoom
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

        # if no route, label is equal to 'no route'
        routes = get_routes_at_stop(stop_lat, stop_lon)
        if not routes:
            self.label_next_bus.config(text="No routes found.")
            return

        # wizard magic...
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

        # if no wizard magic, give no departure details
        if not upcoming_routes:
            self.label_next_bus.config(text="No departures found.")
            return

        # different sort of wizard magic
        upcoming_routes.sort(key=lambda r: r["departure_time"])
        self.next_departure_unix = upcoming_routes[0]["departure_time"]
        self.update_timer() # Start the countdown!

        # loops through the stop info and pulls of the information needed to be displayed...
        # more wizard magic.
        # TH says... "msg_3" is a bit unclear but this seems like this is a string to handle
        # the next three stops in text.
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

    # starts the countdown timer to when the buses arrive.
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

    # creates the messagebox when it is pressed to display all the stop info.
    def show_all_departures(self):
        if self.all_departures:
            messagebox.showinfo("All Departures", self.all_departures)
        else:
            messagebox.showinfo("All Departures", "No departure data available.")

#calls programming loop.
if __name__ == "__main__":
    app = BusStopApp()
    tk.mainloop()