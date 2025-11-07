# AQI Prediction System - Real-Time Forecasting

A software-only ML-based platform for 48-hour AQI prediction using Linear Regression, Random Forest, XGBoost, and LSTM.

## Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Configure API keys in `config/config.py`
3. Run data fetch: `python data_fetch/data_manager.py`
4. Train models: `python training/train_models.py`
5. Start backend: `python backend/app.py`
6. Open dashboard: http://localhost:5000

## Features
- Multi-source API data (CPCB, OpenWeather, IQAir)
- 48-hour AQI forecasting
- Ensemble model selection
- Health alerts
- Interactive web dashboard
- Performance metrics monitoring