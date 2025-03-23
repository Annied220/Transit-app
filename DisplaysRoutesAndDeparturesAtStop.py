import requests
from datetime import datetime, UTC

API_KEY = "[KEY]"  # Replace with your actual API key
# Example latitude and longitude
lattt, lonnn = 45.526168077787894, -73.59506067289408

def get_routes_at_stop(lat, lon, max_distance=150):
    url = "https://external.transitapp.com/v3/public/nearby_routes"
    headers = {"apiKey": API_KEY}
    params = {
        "lat": lat,
        "lon": lon,
        "max_distance": max_distance,
        "should_update_realtime": True
    }

    response = requests.get(url, headers=headers, params=params)
    dave = response.json().get("routes", []) if response.status_code == 200 else []
    return dave

def main():
    routes = get_routes_at_stop(lattt, lonnn, max_distance=1500)
    
    """
    # Extract and print EVERY departure times and route short names
    for route in routes:
        route_short_name = route.get("route_short_name", "Unknown")
        for itinerary in route.get("itineraries", []):
            for schedule in itinerary.get("schedule_items", []):
                timestamp = schedule["departure_time"]
                normal_time = datetime.fromtimestamp(timestamp, UTC).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Route: {route_short_name}, Departure Time: {normal_time}")
    """

    print("For Stop 9TTCT:1166 (I do not even remember what the stop name was at this point)...")
    # Extract and print NEXT departure times and route short names
    for route in routes:
            route_short_name = route.get("route_short_name", "Unknown")
            next_departure = None

            for itinerary in route.get("itineraries", []):
                for schedule in itinerary.get("schedule_items", []):
                    timestamp = schedule["departure_time"]
                    if next_departure is None or timestamp < next_departure:
                        next_departure = timestamp

            if next_departure:
                normal_time = datetime.fromtimestamp(next_departure, UTC).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Route: {route_short_name}, Next Departure Time: {normal_time}")



main()
