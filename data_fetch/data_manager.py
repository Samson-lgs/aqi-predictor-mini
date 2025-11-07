
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from openweather_api import OpenWeatherAPI
from iqair_api import IQAirAPI
from cpcb_api import CPCBAPI
from config.config import DATABASE_URL, CITIES

class DataManager:
    def __init__(self):
        self.db_path = DATABASE_URL.replace("sqlite:///", "")
        self.openweather = OpenWeatherAPI()
        self.iqair = IQAirAPI()
        self.cpcb = CPCBAPI()
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aqi_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source TEXT,
                pm2_5 REAL,
                pm10 REAL,
                no2 REAL,
                so2 REAL,
                co REAL,
                o3 REAL,
                aqi REAL,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_speed REAL,
                UNIQUE(city, timestamp, source)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                prediction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                forecast_hour INTEGER,
                predicted_aqi REAL,
                predicted_pm2_5 REAL,
                model_used TEXT,
                confidence_score REAL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                alert_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                aqi_level INTEGER,
                alert_message TEXT,
                severity TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_aqi_data(self, data, source):
        """Insert AQI data into database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for record in data:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO aqi_data 
                        (city, timestamp, source, pm2_5, pm10, no2, so2, co, o3, aqi, 
                         temperature, humidity, pressure, wind_speed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record.get("city"),
                        record.get("timestamp"),
                        source,
                        record.get("PM2.5"),
                        record.get("PM10"),
                        record.get("NO2"),
                        record.get("SO2"),
                        record.get("CO"),
                        record.get("O3"),
                        record.get("AQI"),
                        record.get("temperature"),
                        record.get("humidity"),
                        record.get("pressure"),
                        record.get("wind_speed"),
                    ))
                except Exception as e:
                    print(f"Error inserting record: {e}")
            
            conn.commit()
            conn.close()
            print(f"Inserted {len(data)} records from {source}")
        
        except Exception as e:
            print(f"Database insertion error: {e}")
    
    def fetch_and_store_data(self):
        """Fetch data from all APIs and store in database"""
        print(f"[{datetime.now()}] Starting data fetch...")
        
        # Fetch from OpenWeather
        try:
            print("Fetching from OpenWeather...")
            ow_data = self.openweather.fetch_all_cities()
            if ow_data["pollution"]:
                self.insert_aqi_data(ow_data["pollution"], "OpenWeather")
            if ow_data["weather"]:
                self.insert_aqi_data(ow_data["weather"], "OpenWeather")
        except Exception as e:
            print(f"OpenWeather error: {e}")
        
        # Fetch from IQAir
        try:
            print("Fetching from IQAir...")
            iqair_data = self.iqair.fetch_all_cities()
            if iqair_data:
                self.insert_aqi_data(iqair_data, "IQAir")
        except Exception as e:
            print(f"IQAir error: {e}")
        
        # Fetch from CPCB
        try:
            print("Fetching from CPCB...")
            cpcb_data = self.cpcb.fetch_station_data()
            if cpcb_data:
                self.insert_aqi_data(cpcb_data, "CPCB")
        except Exception as e:
            print(f"CPCB error: {e}")
        
        print(f"[{datetime.now()}] Data fetch completed!")
    
    def get_training_data(self, days=30):
        """Retrieve historical data for model training"""
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT * FROM aqi_data 
            WHERE timestamp >= datetime('now', '-{days} days')
            ORDER BY city, timestamp
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def export_to_csv(self, filename="aqi_data.csv"):
        """Export data to CSV file"""
        try:
            df = self.get_training_data(days=30)
            df.to_csv(filename, index=False)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Export error: {e}")


if __name__ == "__main__":
    dm = DataManager()
    
    # Fetch data immediately
    dm.fetch_and_store_data()
    
    # Export to CSV for training
    dm.export_to_csv("data/processed/aqi_data.csv")
    
    # Continuous fetch (comment out for one-time execution)
    # while True:
    #     dm.fetch_and_store_data()
    #     time.sleep(3600)  # Fetch every hour
