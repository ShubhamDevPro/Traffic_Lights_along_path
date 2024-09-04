from flask import Flask, render_template, request
from opencage.geocoder import OpenCageGeocode
#from opencage.exceptions import RateLimitExceededError, InvalidInputError

app = Flask(__name__)

# Replace 'YOUR_API_KEY' with your actual OpenCage API key
OPENCAGE_API_KEY = 'YOUR_API_KEY'
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

@app.route('/', methods=['GET', 'POST'])
def index():
    address = None
    error = None
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        results = geocoder.reverse_geocode(float(latitude), float(longitude))
        if results and len(results):
            address = results[0]['formatted']
        else:
            error = "No results found for the given coordinates."
        """
        except RateLimitExceededError:
            error = "Too many requests. Please try again later."
        except InvalidInputError:
            error = "Invalid input. Please check your coordinates."
        except Exception as e:
            error = f"An error occurred: {str(e)}"
        """
    return render_template('index.html', address=address, error=error)

if __name__ == '__main__':
    app.run(debug=True)