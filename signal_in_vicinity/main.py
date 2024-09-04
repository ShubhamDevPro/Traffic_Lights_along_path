from flask import Flask, render_template, request
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

app = Flask(__name__)

geolocator = Nominatim(user_agent="traffic_lights_app")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        location = request.form['location']
        coordinates = get_coordinates(location)

        if coordinates:
            latitude, longitude = coordinates

            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["highway"="traffic_signals"]
              (around:3000, {latitude}, {longitude}); 
            );
            out body;
            >;
            out skel qt;
            """

            response = requests.get("http://overpass-api.de/api/interpreter", params={"data": overpass_query})
            data = response.json()

            # Extract coordinates of traffic signals
            traffic_signals = [(element['lat'], element['lon']) for element in data['elements']]

            return render_template('index.html', traffic_signals=traffic_signals, location=location)
        else:
            return render_template('index.html', error="Location not found.")

    return render_template('index.html')

def get_coordinates(address):
    """Use Nominatim geocoding service to get coordinates for an address."""
    try:
        location = geolocator.geocode(address)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None

if __name__ == '__main__':
    app.run(debug=True)