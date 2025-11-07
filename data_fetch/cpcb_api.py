import requests
import json
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import CPCB_API_KEY, CITIES

class CPCBAPI:
    def __init__(self):
        self.api_key = CPCB_API_KEY
        self.base_url = "http://api.data.gov.in/resource/3d6880c4-98d4-48d6-88d0-2603019c4971"
        
    def fetch_station_data(self):
        try:
            params = {"api-key": self.api_key, "format": "json", "limit": 500}
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                city_data = {}
                for record in records:
                    try:
                        city = record.get("City", "Unknown")
                        if city in CITIES:
                            if city not in city_data:
                                city_data[city] = {
                                    "city": city,
                                    "timestamp": datetime.now().isoformat(),
                                    "source": "CPCB",
                                    "PM2.5": None, "PM10": None, "NO2": None,
                                    "SO2": None, "CO": None, "O3": None, "AQI": None,
                                }
                            
                            if record.get("Pollutant_ID") == "PM2.5":
                                city_data[city]["PM2.5"] = float(record.get("Pollutant_Max", 0) or 0)
                            elif record.get("Pollutant_ID") == "PM10":
                                city_data[city]["PM10"] = float(record.get("Pollutant_Max", 0) or 0)
                            # Add other pollutants similarly
                            
                            city_data[city]["AQI"] = float(record.get("AQI", 0) or 0)
                    except:
                        continue
                
                return list(city_data.values())
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []
