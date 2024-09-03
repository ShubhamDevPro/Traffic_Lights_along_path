from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

app = Flask(__name__)
geolocator = Nominatim(user_agent="my_location_finder")

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
        address = request.form['address']
        coords = get_coordinates(address)

        if coords:
            return render_template('index.html', coords=coords, address=address)
        else:
            return "Address could not be geocoded"
    return render_template('index.html')

@app.route('/get_location', methods=['POST'])
def get_location():
    address = request.json['address']
    coords = get_coordinates(address)

    if coords:
        return jsonify({"latitude": coords[0], "longitude": coords[1]})
    else:
        return jsonify({"error": "Address could not be geocoded"}), 400

if __name__ == '__main__':
    app.run(debug=True)