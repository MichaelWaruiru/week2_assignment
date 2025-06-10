import streamlit as st
import pandas as pd
import numpy as np
# import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

# Load and preprocess data
gen_df = pd.read_csv("solar_power_generation.csv")
weather_df = pd.read_csv("weather_sensor_data.csv")

# Convert datetime
gen_df['DATE_TIME'] = pd.to_datetime(gen_df['DATE_TIME'])
weather_df['DATE_TIME'] = pd.to_datetime(weather_df['DATE_TIME'])

# Merge datasets using nearest timestamp match
merged_df = pd.merge_asof(
    gen_df.sort_values("DATE_TIME"),
    weather_df.sort_values("DATE_TIME"),
    on="DATE_TIME",
    direction="nearest"
)

# Drop missing and prepare features
def prepare_training_data(df):
    df = df.dropna()
    df['hour'] = df['DATE_TIME'].dt.hour
    df['day'] = df['DATE_TIME'].dt.day
    features = ['AMBIENT_TEMPERATURE', 'MODULE_TEMPERATURE', 'IRRADIATION', 'hour', 'day']
    X = df[features]
    y = df['DC_POWER']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, y, scaler, features

X_scaled, y, scaler, features = prepare_training_data(merged_df)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# Streamlit app UI
st.title("🌞 Solar DC Power Prediction (SDG 7)")
st.markdown("Enter environmental and time conditions below:")

ambient_temp = st.slider("Ambient Temperature (°C)", 0.0, 60.0, 25.0)
module_temp = st.slider("Module Temperature (°C)", 0.0, 80.0, 40.0)
irradiation = st.slider("Irradiation (W/m²)", 0.0, 1300.0, 600.0)
hour = st.slider("Hour of Day", 0, 23, 12)
day = st.slider("Day of Month", 1, 31, 15)

# Prepare input and predict
user_input = pd.DataFrame([[ambient_temp, module_temp, irradiation, hour, day]], columns=features)
user_input_scaled = scaler.transform(user_input)
prediction = model.predict(user_input_scaled)[0]

st.success(f"🔋 Predicted DC Power Output: {prediction:.2f} W")

st.caption("Model: Random Forest Regressor | Trained on Solar Power Generation Data")
