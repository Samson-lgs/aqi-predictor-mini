import requests
import json
from datetime import datetime
from config.config import IQAIR_API_KEY, CITIES

class IQAirAPI:
    def __init__(self):
        self.api_key = IQAIR_API_KEY
        self.base_url = "http://api.waqi.info"
        
    def fetch_city_data(self, city):
        """Fetch AQI data from IQAir/WAQI for a city"""
        try:
            # Map city names to WAQI city codes
            city_map = {
                "Delhi": "delhi",
                "Mumbai": "mumbai",
                "Bangalore": "bangalore",
                "Kolkata": "kolkata",
                "Chennai": "chennai",
                "Hyderabad": "hyderabad",
                "Pune": "pune",
                "Ahmedabad": "ahmedabad",
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
            
            print(f"Error fetching IQAir data for {city}: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Exception in IQAir fetch for {city}: {e}")
            return None
    
    def fetch_all_cities(self):
        """Fetch data for all configured cities"""
        results = []
        
        for city in CITIES.keys():
            data = self.fetch_city_data(city)
            if data:
                results.append(data)
        
        return results


if __name__ == "__main__":
    iqair = IQAirAPI()
    data = iqair.fetch_all_cities()
    print(json.dumps(data, indent=2))
