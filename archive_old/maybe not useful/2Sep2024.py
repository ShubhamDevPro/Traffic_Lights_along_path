import requests
import json
import folium
from selenium import webdriver
from PIL import Image
import time

# Define the coordinates
start_coords = [28.677035404623453, 77.3467789984989]
end_coords = [28.670597613675323, 77.41535338244188]

# Construct the URL
url = f"http://127.0.0.1:5001/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?steps=true"

# Make the request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Create a map centered at the start location
    m = folium.Map(location=start_coords, zoom_start=13)
    
    # Add markers for the start and end locations
    folium.Marker(start_coords, popup='Start', icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(end_coords, popup='End', icon=folium.Icon(color='red')).add_to(m)
    
    # Extract the route coordinates
    route_coords = [(step['maneuver']['location'][1], step['maneuver']['location'][0]) for step in data['routes'][0]['legs'][0]['steps']]
    
    # Add the route to the map
    folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.7).add_to(m)
    
    # Save the map as an HTML file
    map_file = 'route_map.html'
    m.save(map_file)
    
    # Use Selenium to open the HTML file and save it as a PNG
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(800, 600)
    driver.get(f'file://{map_file}')
    
    # Give the map some time to load
    time.sleep(5)
    
    # Save the map as a PNG file
    png_file = 'route_map.png'
    driver.save_screenshot(png_file)
    driver.quit()
    
    # Convert the PNG file to a JPEG file
    jpeg_file = 'route_map.jpg'
    Image.open(png_file).convert('RGB').save(jpeg_file, 'JPEG')
    
    print(f"Map saved as {jpeg_file}")
else:
    print(f"Error: {response.status_code}")