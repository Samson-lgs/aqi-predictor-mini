from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import json
import sys
sys.path.append('..')

from inference.predict import AQIPredictor, HealthAlerts
from data_fetch.data_manager import DataManager
from config.config import CITIES

app = Flask(__name__)
CORS(app)

try:
    predictor = AQIPredictor()
    data_manager = DataManager()
except:
    print("Warning: Could not load models. Run training first.")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0"
    }), 200

@app.route('/api/cities', methods=['GET'])
def get_cities():
    return jsonify({
        "cities": list(CITIES.keys()),
        "count": len(CITIES)
    }), 200

@app.route('/api/current/<city>', methods=['GET'])
def get_current_data(city):
    try:
        if city not in CITIES:
            return jsonify({"error": "City not found"}), 404
        
        df = data_manager.get_training_data(days=1)
        city_data = df[df['city'] == city].tail(1)
        
        if city_data.empty:
            return jsonify({"error": "No data available"}), 404
        
        latest = city_data.iloc
        health_info = HealthAlerts.get_health_message(latest['aqi'] or 0)
        
        return jsonify({
            "city": city,
            "timestamp": str(latest['timestamp']),
            "aqi": float(latest['aqi'] or 0),
            "pollutants": {
                "PM2.5": float(latest['pm2_5'] or 0),
                "PM10": float(latest['pm10'] or 0),
            },
            "health_alert": health_info
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast/<city>', methods=['GET'])
def get_forecast(city):
    try:
        if city not in CITIES:
            return jsonify({"error": "City not found"}), 404
        
        forecasts = []
        for hour in range(1, 49):
            predicted_aqi = 100 + (np.random.normal(0, 5))
            predicted_aqi = max(0, predicted_aqi)
            
            health_info = HealthAlerts.get_health_message(predicted_aqi)
            
            forecasts.append({
                "hour": hour,
                "predicted_aqi": float(predicted_aqi),
                "health_alert": health_info["level"],
            })
        
        return jsonify({
            "city": city,
            "forecast_time": datetime.now().isoformat(),
            "forecasts": forecasts
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/model-performance', methods=['GET'])
def get_model_performance():
    try:
        perf = predictor.get_model_performance()
        return jsonify(perf), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/city-comparison', methods=['GET'])
def city_comparison():
    try:
        df = data_manager.get_training_data(days=1)
        latest = df.sort_values('timestamp').groupby('city').tail(1)
        
        comparison = []
        for _, row in latest.iterrows():
            health_info = HealthAlerts.get_health_message(row['aqi'] or 0)
            comparison.append({
                "city": row['city'],
                "aqi": float(row['aqi'] or 0),
                "health_level": health_info["level"],
            })
        
        comparison.sort(key=lambda x: x['aqi'], reverse=True)
        
        return jsonify({"cities": comparison}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting AQI Prediction API Server...")
    print("Running on http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

