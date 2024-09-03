from flask import Flask, render_template, request, jsonify
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

app = Flask(__name__)
OSRM_BASE_URL = 'http://127.0.0.1:5001'
geolocator = Nominatim(user_agent="my_route_finder")

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_address = request.form['start_address']
        end_address = request.form['end_address']
        start_coords = get_coordinates(start_address)
        end_coords = get_coordinates(end_address)
        
        if start_coords and end_coords:
            osrm_url = f'{OSRM_BASE_URL}/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?steps=true&geometries=geojson'
            
            response = requests.get(osrm_url)
            if response.status_code == 200:
                route_data = response.json()
                return render_template('index.html', route_data=route_data, 
                                       start_address=start_address, 
                                       end_address=end_address)
            else:
                return "Error getting route from OSRM"
        else:
            return "One or both addresses could not be geocoded"
    return render_template('index.html')

@app.route('/get_route', methods=['POST'])
def get_route():
    start_address = request.json['start_address']
    end_address = request.json['end_address']
    
    start_coords = get_coordinates(start_address)
    end_coords = get_coordinates(end_address)
    
    if start_coords and end_coords:
        osrm_url = f'{OSRM_BASE_URL}/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?steps=true&geometries=geojson'
        
        response = requests.get(osrm_url)
        if response.status_code == 200:
            route_data = response.json()
            return jsonify(route_data)
        else:
            return jsonify({"error": "Error getting route from OSRM"}), 500
    else:
        return jsonify({"error": "One or both addresses could not be geocoded"}), 400

if __name__ == '__main__':
    app.run(debug=True,port = 5009)