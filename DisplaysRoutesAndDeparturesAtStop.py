import requests # needed for API functioning to work.
from datetime import datetime, UTC, timedelta # https://docs.python.org/3/library/datetime.html#datetime.datetime

# -4 hr to account for EST # converts to 12-hr clock

# CHANGELOG!
# moved date to its own variable
# Added API reader to keep the API off future code...
# so that it will just reference a txt file in the same folder named "API.txt"

with open("API.txt", "r") as file: API_KEY = file.read() # Read's API.txt to keep the API out of the code.
latitude, longitude = 41.53893285402787, -72.80120743546017 #debug - meriden station commuter parking
# 45.526168077787894, -73.59506067289408 # debug - I do not remember where this is... toad's place?

def get_routes_at_stop(lat, lon, max_distance=1500):
    url = "https://external.transitapp.com/v3/public/nearby_routes"
    headers = { "apiKey": API_KEY   } # API needs the key to be in the header.
    params = {  "lat": lat,
                "lon": lon,
                "max_distance": max_distance,
                "should_update_realtime": True  } # only needs lat and lon to work.
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("routes", []) if response.status_code == 200 else [] # if 200, API works. else it didn't.

def display_routes_at_stop(): # loops for days.
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

display_routes_at_stop()
