import requests # https://www.w3schools.com/python/module_requests.asp

def get_nearby_bus_stops(lat, lon, api_key, max_distance=1500, stop_filter="Routable",
                         pickup_dropoff_filter="Everything", language="en"):
    # URL for the Transit App API endpoint
    url = "https://external.transitapp.com/v3/public/nearby_routes"

    # Headers for the request (including Accept-Language header)
    headers = {
        #"Accept-Language": language  # You can change this language if needed
        "apiKey": api_key  # Add your API key here
    }

    # Parameters to be sent in the API request (latitude, longitude, max_distance, etc.)
    params = {
        "lat": lat,
        "lon": lon,
        #"max_distance": max_distance,
        #"stop_filter": stop_filter,
        "pickup_dropoff_filter": pickup_dropoff_filter,

    }

    # Send the GET request to the Transit App API
    try:
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            # You can process 'data' to extract the nearby bus stops
            return data
        else:
            print(f"Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
latitude = 41.6901407  # Example latitude
longitude = -72.7664725  # Example longitude
#CCSU
api_key = "[KEYTEXT]" #KEY GOES HERE

# Call the function with the desired parameters
nearby_bus_stops = get_nearby_bus_stops(latitude, longitude, api_key)

# Check the results
if nearby_bus_stops:
    print("Nearby Bus Stops: ")
    print(nearby_bus_stops)
