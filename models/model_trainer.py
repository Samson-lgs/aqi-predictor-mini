import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.performance_metrics = {}
        
    def load_features(self, csv_path):
        """Load feature engineered data"""
        df = pd.read_csv(csv_path)
        return df
    
    def prepare_data(self, df):
        """Split data into train, validation, test sets"""
        # Separate features and target
        X = df.drop(['city', 'target_aqi'], axis=1)
        y = df['target_aqi']
        
        # Time-aware split (80-10-10)
        train_size = int(len(df) * 0.8)
        val_size = int(len(df) * 0.1)
        
        X_train = X[:train_size]
        y_train = y[:train_size]
        
        X_val = X[train_size:train_size+val_size]
        y_val = y[train_size:train_size+val_size]
        
        X_test = X[train_size+val_size:]
        y_test = y[train_size+val_size:]
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def train_linear_regression(self, X_train, y_train, X_val, y_val):
        """Train Linear Regression model"""
        print("Training Linear Regression...")
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_val = model.predict(X_val)
        r2 = r2_score(y_val, y_pred_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        mae = mean_absolute_error(y_val, y_pred_val)
        
        metrics = {"r2": r2, "rmse": rmse, "mae": mae}
        print(f"Linear Regression - R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return model, metrics
    
    def train_random_forest(self, X_train, y_train, X_val, y_val):
        """Train Random Forest model"""
        print("Training Random Forest...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_val = model.predict(X_val)
        r2 = r2_score(y_val, y_pred_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        mae = mean_absolute_error(y_val, y_pred_val)
        
        metrics = {"r2": r2, "rmse": rmse, "mae": mae}
        print(f"Random Forest - R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return model, metrics
    
    def train_xgboost(self, X_train, y_train, X_val, y_val):
        """Train XGBoost model"""
        print("Training XGBoost...")
        model = XGBRegressor(
            n_estimators=100,
            max_depth=7,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        
        # Evaluate
        y_pred_val = model.predict(X_val)
        r2 = r2_score(y_val, y_pred_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        mae = mean_absolute_error(y_val, y_pred_val)
        
        metrics = {"r2": r2, "rmse": rmse, "mae": mae}
        print(f"XGBoost - R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return model, metrics
    
    def train_lstm(self, X_train, y_train, X_val, y_val):
        """Train LSTM model"""
        print("Training LSTM...")
        
        # Reshape data for LSTM (samples, timesteps, features)
        X_train_lstm = X_train.values.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_val_lstm = X_val.values.reshape((X_val.shape[0], X_val.shape[1], 1))
        
        model = Sequential([
            LSTM(64, activation='relu', input_shape=(X_train_lstm.shape[1], 1)),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        history = model.fit(
            X_train_lstm, y_train,
            epochs=50,
            batch_size=32,
            validation_data=(X_val_lstm, y_val),
            callbacks=[early_stop],
            verbose=0
        )
        
        # Evaluate
        y_pred_val = model.predict(X_val_lstm, verbose=0).flatten()
        r2 = r2_score(y_val, y_pred_val)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))
        mae = mean_absolute_error(y_val, y_pred_val)
        
        metrics = {"r2": r2, "rmse": rmse, "mae": mae}
        print(f"LSTM - R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
        
        return model, metrics
    
    def train_all_models(self, csv_path):
        """Train all models and save best performers"""
        print("Loading and preparing data...")
        df = self.load_features(csv_path)
        X_train, X_val, X_test, y_train, y_val, y_test = self.prepare_data(df)
        
        # Train all models
        lr_model, lr_metrics = self.train_linear_regression(X_train, y_train, X_val, y_val)
        rf_model, rf_metrics = self.train_random_forest(X_train, y_train, X_val, y_val)
        xgb_model, xgb_metrics = self.train_xgboost(X_train, y_train, X_val, y_val)
        lstm_model, lstm_metrics = self.train_lstm(X_train, y_train, X_val, y_val)
        
        # Store models and metrics
        self.models = {
            "linear_regression": lr_model,
            "random_forest": rf_model,
            "xgboost": xgb_model,
            "lstm": lstm_model
        }
        
        self.performance_metrics = {
            "linear_regression": lr_metrics,
            "random_forest": rf_metrics,
            "xgboost": xgb_metrics,
            "lstm": lstm_metrics
        }
        
        # Save models
        self.save_models()
        
        # Print summary
        self.print_summary()
        
        return self.models, self.performance_metrics
    
    def save_models(self):
        """Save trained models to disk"""
        for model_name, model in self.models.items():
            if model_name == "lstm":
                model.save(f"saved_models/{model_name}_model.h5")
            else:
                joblib.dump(model, f"saved_models/{model_name}_model.pkl")
        
        # Save metrics
        with open("saved_models/metrics.json", "w") as f:
            json.dump(self.performance_metrics, f, indent=2)
        
        print("Models saved successfully!")
    
    def print_summary(self):
        """Print model performance summary"""
        print("\n" + "="*60)
        print("MODEL PERFORMANCE SUMMARY")
        print("="*60)
        
        for model_name, metrics in self.performance_metrics.items():
            print(f"\n{model_name.upper()}:")
            print(f"  R² Score: {metrics['r2']:.4f}")
            print(f"  RMSE: {metrics['rmse']:.4f}")
            print(f"  MAE: {metrics['mae']:.4f}")
        
        # Find best model
        best_model = max(self.performance_metrics.items(), 
                        key=lambda x: x[1]['r2'])
        print(f"\n✓ Best Model: {best_model[0]} (R² = {best_model[1]['r2']:.4f})")
        print("="*60)


if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.train_all_models("data/processed/aqi_features.csv")
