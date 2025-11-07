import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENWEATHER_API_KEY = "528f129d20a5e514729cbf24b2449e44"
IQAIR_API_KEY = "102c31e0-0f3c-4865-b4f3-2b4a57e78c40"
CPCB_API_KEY = "579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aqi_data.db")

# Cities to Monitor
CITIES = {
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
}

# Forecast Horizon
FORECAST_HOURS = 48

# Model Parameters
MODEL_PARAMS = {
    "test_size": 0.2,
    "validation_size": 0.15,
    "random_state": 42,
}

# Pollutants to Track
POLLUTANTS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]

# Weather Features
WEATHER_FEATURES = ["temperature", "humidity", "wind_speed", "pressure"]

# Performance Thresholds
TARGET_R2 = 0.85
TARGET_RMSE = 25
TARGET_MAE = 15