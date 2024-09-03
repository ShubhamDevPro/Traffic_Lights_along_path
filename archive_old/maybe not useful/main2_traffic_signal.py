import folium
from geopy.geocoders import Nominatim
import requests
import json
import overpy

def get_route_map(start, end, api_key):
    print("Starting route map generation...")

    # Initialize geocoder and overpy
    geolocator = Nominatim(user_agent="my_route_app")
    api = overpy.Overpass()

    # Geocode locations
    print(f"Geocoding start location: {start}")
    start_location = geolocator.geocode(start)
    print(f"Geocoding end location: {end}")
    end_location = geolocator.geocode(end)

    if not start_location or not end_location:
        print("Error: Unable to geocode one or both locations.")
        return None

    print(f"Start coordinates: {start_location.latitude}, {start_location.longitude}")
    print(f"End coordinates: {end_location.latitude}, {end_location.longitude}")

    # Create map
    print("Creating base map...")
    m = folium.Map(location=[start_location.latitude, start_location.longitude], zoom_start=6)

    # Use OpenRouteService Directions API for driving-car
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        "coordinates": [
            [start_location.longitude, start_location.latitude],
            [end_location.longitude, end_location.latitude]
        ]
    }

    print("Sending request to OpenRouteService API...")
    response = requests.post(url, json=body, headers=headers)
    
    print(f"API Response Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error: API request failed with status code {response.status_code}")
        print(f"Response content: {response.text}")
        return None

    routes = response.json()

    # Check if 'features' key exists in the response
    if 'features' in routes and routes['features']:
        print("Route data received successfully.")
        # Add route to map
        route_coords = [[coord[1], coord[0]] for coord in routes['features'][0]['geometry']['coordinates']]
        folium.PolyLine(route_coords, weight=5, color='red').add_to(m)

        # Get bounding box of the route
        lats, lons = zip(*route_coords)
        bbox = f"{min(lats)},{min(lons)},{max(lats)},{max(lons)}"

        # Query for traffic signals along the route
        print("Querying for traffic signals...")
        query = f"""
        [out:json];
        (
          node["highway"="traffic_signals"]({bbox});
        );
        out body;
        """
        result = api.query(query)

        # Add traffic signal markers
        for node in result.nodes:
            folium.Marker(
                [node.lat, node.lon],
                popup="Traffic Signal",
                icon=folium.Icon(color='green', icon='traffic-light', prefix='fa')
            ).add_to(m)

    else:
        print("Error: Unable to retrieve route information from the API response.")
        print(f"API Response: {json.dumps(routes, indent=2)}")
        return None

    # Add markers for start and end
    folium.Marker([start_location.latitude, start_location.longitude], popup='Start').add_to(m)
    folium.Marker([end_location.latitude, end_location.longitude], popup='End').add_to(m)

    print("Map generation complete.")
    return m

# Example usage
start_location = "Karkarduma Court"
end_location = "Tughlakabad Metro Station"
api_key = "5b3ce3597851110001cf6248c92474800b4e40238f8d6432ff82746a"  # Your API key

print("Calling get_route_map function...")
route_map = get_route_map(start_location, end_location, api_key)

if route_map:
    output_file = "route_map.html"
    route_map.save(output_file)
    print(f"Map saved to {output_file}")
else:
    print("Failed to generate route map.")