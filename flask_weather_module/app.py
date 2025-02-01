from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

# Free weather API (WeatherStack)
API_KEY = "a7fee96e43797770203643567624c26d"
BASE_URL = "http://api.weatherstack.com/current"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form['city']
    params = {
        'access_key': API_KEY,
        'query': city
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if "error" in data:
        return jsonify({"error": "City not found"})
    
    weather_info = {
        "city": data["location"]["name"],
        "temperature": data["current"]["temperature"],
        "humidity": data["current"]["humidity"],
        "wind_speed": data["current"]["wind_speed"],
        "weather": data["current"]["weather_descriptions"][0],
    }
    
    return render_template('index.html', weather=weather_info)

if __name__ == '__main__':
    app.run(debug=True)