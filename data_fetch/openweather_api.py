import requests
import json
from datetime import datetime
from config.config import OPENWEATHER_API_KEY, CITIES

class OpenWeatherAPI:
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.pollution_url = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.weather_url = "http://api.openweathermap.org/data/2.5/weather"
        
    def fetch_pollution_data(self, city, lat, lon):
        try:
            params = {"lat": lat, "lon": lon, "appid": self.api_key}
            response = requests.get(self.pollution_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pollution = data.get("list", [{}]).get("components", {})
                
                return {
                    "city": city,
                    "timestamp": datetime.now().isoformat(),
                    "source": "OpenWeather",
                    "PM2.5": pollution.get("pm2_5"),
                    "PM10": pollution.get("pm10"),
                    "NO2": pollution.get("no2"),
                    "SO2": pollution.get("so2"),
                    "CO": pollution.get("co"),
                    "O3": pollution.get("o3"),
                }
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def fetch_weather_data(self, city, lat, lon):
        try:
            params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"}
            response = requests.get(self.weather_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "city": city,
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "timestamp": datetime.now().isoformat(),
                    "source": "OpenWeather",
                }
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def fetch_all_cities(self):
        results = {"pollution": [], "weather": []}
        for city, coords in CITIES.items():
            pollution_data = self.fetch_pollution_data(city, coords["lat"], coords["lon"])
            weather_data = self.fetch_weather_data(city, coords["lat"], coords["lon"])
            if pollution_data:
                results["pollution"].append(pollution_data)
            if weather_data:
                results["weather"].append(weather_data)
        return results
