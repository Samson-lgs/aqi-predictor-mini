import requests
import json
from datetime import datetime
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.config import IQAIR_API_KEY, CITIES

class IQAirAPI:
    def __init__(self):
        self.api_key = IQAIR_API_KEY
        self.base_url = "http://api.waqi.info"
        
    def fetch_city_data(self, city):
        try:
            city_map = {
                "Delhi": "delhi", "Mumbai": "mumbai", "Bangalore": "bangalore",
                "Kolkata": "kolkata", "Chennai": "chennai", "Hyderabad": "hyderabad",
                "Pune": "pune", "Ahmedabad": "ahmedabad",
            }
            
            city_code = city_map.get(city, city.lower())
            params = {"token": self.api_key}
            url = f"{self.base_url}/feed/{city_code}/index.json"
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    current_data = data["data"]["current"]["pollution"]
                    return {
                        "city": city,
                        "timestamp": datetime.now().isoformat(),
                        "source": "IQAir",
                        "PM2.5": current_data.get("pm25"),
                        "PM10": current_data.get("pm10"),
                        "NO2": current_data.get("no2"),
                        "SO2": current_data.get("so2"),
                        "CO": current_data.get("co"),
                        "O3": current_data.get("o3"),
                        "AQI": current_data.get("aqius"),
                    }
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def fetch_all_cities(self):
        results = []
        for city in CITIES.keys():
            data = self.fetch_city_data(city)
            if data:
                results.append(data)
        return results
