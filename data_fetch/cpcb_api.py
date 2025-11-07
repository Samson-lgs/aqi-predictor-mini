
import requests
import json
from datetime import datetime
from config.config import CPCB_API_KEY, CITIES

class CPCBAPI:
    def __init__(self):
        self.api_key = CPCB_API_KEY
        self.base_url = "http://api.data.gov.in/resource/3d6880c4-98d4-48d6-88d0-2603019c4971"
        
    def fetch_station_data(self):
        """Fetch AQI data from CPCB portal"""
        try:
            params = {
                "api-key": self.api_key,
                "format": "json",
                "limit": 500,
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                # Parse and organize by city
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
                                    "PM2.5": None,
                                    "PM10": None,
                                    "NO2": None,
                                    "SO2": None,
                                    "CO": None,
                                    "O3": None,
                                    "AQI": None,
                                }
                            
                            # Extract pollutant values
                            if record.get("Pollutant_ID") == "PM2.5":
                                city_data[city]["PM2.5"] = float(record.get("Pollutant_Max", 0) or 0)
                            elif record.get("Pollutant_ID") == "PM10":
                                city_data[city]["PM10"] = float(record.get("Pollutant_Max", 0) or 0)
                            elif record.get("Pollutant_ID") == "NO2":
                                city_data[city]["NO2"] = float(record.get("Pollutant_Max", 0) or 0)
                            elif record.get("Pollutant_ID") == "SO2":
                                city_data[city]["SO2"] = float(record.get("Pollutant_Max", 0) or 0)
                            elif record.get("Pollutant_ID") == "CO":
                                city_data[city]["CO"] = float(record.get("Pollutant_Max", 0) or 0)
                            elif record.get("Pollutant_ID") == "O3":
                                city_data[city]["O3"] = float(record.get("Pollutant_Max", 0) or 0)
                            
                            city_data[city]["AQI"] = float(record.get("AQI", 0) or 0)
                    
                    except Exception as e:
                        print(f"Error parsing CPCB record: {e}")
                        continue
                
                return list(city_data.values())
            
            else:
                print(f"Error fetching CPCB data: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"Exception in CPCB fetch: {e}")
            return []


if __name__ == "__main__":
    cpcb = CPCBAPI()
    data = cpcb.fetch_station_data()
    print(json.dumps(data, indent=2))
