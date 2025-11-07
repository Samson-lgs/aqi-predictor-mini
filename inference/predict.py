import pandas as pd
import numpy as np
import joblib
from tensorflow import keras
import json
from datetime import datetime
import sqlite3

class AQIPredictor:
    def __init__(self):
        self.lr_model = joblib.load("saved_models/linear_regression_model.pkl")
        self.rf_model = joblib.load("saved_models/random_forest_model.pkl")
        self.xgb_model = joblib.load("saved_models/xgboost_model.pkl")
        self.lstm_model = keras.models.load_model("saved_models/lstm_model.h5")
        
        with open("saved_models/metrics.json", "r") as f:
            self.metrics = json.load(f)
        
        self.best_model_name = max(self.metrics.items(), key=lambda x: x['r2'])
        self.best_model = self._get_model(self.best_model_name)
    
    def _get_model(self, model_name):
        models = {
            "linear_regression": self.lr_model,
            "random_forest": self.rf_model,
            "xgboost": self.xgb_model,
            "lstm": self.lstm_model
        }
        return models.get(model_name)
    
    def predict(self, features, model_name=None):
        if model_name is None:
            model_name = self.best_model_name
        
        model = self._get_model(model_name)
        
        if model_name == "lstm":
            features_reshaped = features.values.reshape((features.shape, features.shape, 1))
            prediction = model.predict(features_reshaped, verbose=0)
        else:
            prediction = model.predict(features)
        
        return prediction
    
    def get_model_performance(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "models": self.metrics,
            "best_model": {
                "name": self.best_model_name,
                "metrics": self.metrics[self.best_model_name]
            }
        }

class HealthAlerts:
    @staticmethod
    def get_health_message(aqi):
        aqi = float(aqi)
        
        if aqi <= 50:
            return {
                "level": "Good",
                "severity": "low",
                "message": "Air quality is satisfactory!",
                "recommendation": "Enjoy outdoor activities!"
            }
        elif aqi <= 100:
            return {
                "level": "Moderate",
                "severity": "low",
                "message": "Air quality is acceptable.",
                "recommendation": "Sensitive groups should limit outdoor activities."
            }
        elif aqi <= 150:
            return {
                "level": "Unhealthy for Sensitive Groups",
                "severity": "medium",
                "message": "Members of sensitive groups may experience health effects.",
                "recommendation": "Sensitive groups should limit outdoor activities."
            }
        elif aqi <= 200:
            return {
                "level": "Unhealthy",
                "severity": "high",
                "message": "Health alert! Everyone may experience health effects.",
                "recommendation": "Limit outdoor activities. Wear N95 masks if going outside."
            }
        elif aqi <= 300:
            return {
                "level": "Very Unhealthy",
                "severity": "critical",
                "message": "Health warning! Serious health effects possible.",
                "recommendation": "Avoid outdoor activities. Stay indoors."
            }
        else:
            return {
                "level": "Hazardous",
                "severity": "critical",
                "message": "Health alarm! It's unsafe to go outside.",
                "recommendation": "Stay indoors. Close all windows and doors."
            }
