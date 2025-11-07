import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineering:
    def __init__(self):
        self.scaler = StandardScaler()
        self.min_max_scaler = MinMaxScaler()
    
    def load_and_prepare_data(self, csv_path):
        """Load CSV and perform initial preprocessing"""
        df = pd.read_csv(csv_path)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(['city', 'timestamp']).reset_index(drop=True)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Remove outliers
        df = self.remove_outliers(df)
        
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values using forward fill and interpolation"""
        for city in df['city'].unique():
            city_mask = df['city'] == city
            
            # Forward fill for pollutants
            pollutants = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3']
            for pollutant in pollutants:
                df.loc[city_mask, pollutant] = df.loc[city_mask, pollutant].fillna(
                    method='ffill'
                ).fillna(method='bfill').interpolate()
            
            # Forward fill for weather
            weather = ['temperature', 'humidity', 'pressure', 'wind_speed']
            for feature in weather:
                df.loc[city_mask, feature] = df.loc[city_mask, feature].fillna(
                    method='ffill'
                ).fillna(method='bfill').interpolate()
        
        # Fill remaining NaN with mean
        df = df.fillna(df.mean(numeric_only=True))
        
        return df
    
    def remove_outliers(self, df):
        """Remove outliers using IQR method"""
        pollutants = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3']
        
        for pollutant in pollutants:
            if pollutant in df.columns:
                Q1 = df[pollutant].quantile(0.25)
                Q3 = df[pollutant].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Replace outliers with median
                median = df[pollutant].median()
                mask = (df[pollutant] < lower_bound) | (df[pollutant] > upper_bound)
                df.loc[mask, pollutant] = median
        
        return df
    
    def extract_temporal_features(self, df):
        """Extract time-based features from timestamp"""
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['day'] = df['timestamp'].dt.day
        
        # Create cyclical features for hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Create cyclical features for day of week
        df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Seasonal features
        df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
        df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
        
        return df
    
    def create_lagged_features(self, df, lags=[1, 6, 24]):
        """Create lagged features for time series"""
        pollutants = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3']
        
        for city in df['city'].unique():
            city_mask = df['city'] == city
            city_df = df[city_mask]
            
            for pollutant in pollutants:
                for lag in lags:
                    lag_col_name = f'{pollutant}_lag_{lag}'
                    df.loc[city_mask, lag_col_name] = city_df[pollutant].shift(lag)
        
        return df
    
    def create_rolling_features(self, df, windows=[6, 24]):
        """Create rolling statistics"""
        pollutants = ['pm2_5', 'pm10', 'no2', 'so2', 'co', 'o3']
        
        for city in df['city'].unique():
            city_mask = df['city'] == city
            
            for pollutant in pollutants:
                for window in windows:
                    # Rolling mean
                    mean_col = f'{pollutant}_rolling_mean_{window}'
                    df.loc[city_mask, mean_col] = df.loc[city_mask, pollutant].rolling(
                        window=window, min_periods=1
                    ).mean()
                    
                    # Rolling std
                    std_col = f'{pollutant}_rolling_std_{window}'
                    df.loc[city_mask, std_col] = df.loc[city_mask, pollutant].rolling(
                        window=window, min_periods=1
                    ).std().fillna(0)
        
        return df
    
    def create_target_variable(self, df, forecast_hours=1):
        """Create target variable for forecasting (shift AQI forward)"""
        for city in df['city'].unique():
            city_mask = df['city'] == city
            df.loc[city_mask, 'target_aqi'] = df.loc[city_mask, 'aqi'].shift(-forecast_hours)
        
        # Remove rows where target is NaN
        df = df.dropna(subset=['target_aqi'])
        
        return df
    
    def normalize_features(self, X_train, X_test):
        """Normalize features using training data"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        return X_train_scaled, X_test_scaled
    
    def prepare_final_dataset(self, csv_path):
        """Complete pipeline for data preparation"""
        print("Loading data...")
        df = self.load_and_prepare_data(csv_path)
        
        print("Extracting temporal features...")
        df = self.extract_temporal_features(df)
        
        print("Creating lagged features...")
        df = self.create_lagged_features(df)
        
        print("Creating rolling features...")
        df = self.create_rolling_features(df)
        
        print("Creating target variable...")
        df = self.create_target_variable(df)
        
        # Drop columns not needed for modeling
        drop_cols = ['timestamp', 'source', 'id']
        df = df.drop(columns=[c for c in drop_cols if c in df.columns])
        
        print(f"Final dataset shape: {df.shape}")
        
        return df


if __name__ == "__main__":
    fe = FeatureEngineering()
    df = fe.prepare_final_dataset("data/processed/aqi_data.csv")
    df.to_csv("data/processed/aqi_features.csv", index=False)
    print("Features saved!")