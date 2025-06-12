import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Golf – Korrigeret Slaglængde")

st.markdown("Denne app justerer dine slaglængder baseret på **lokalt vejr og højde**.")

# --- API-indstillinger ---
WEATHER_API_KEY = "ab123184d6aa2b73b4114f9045ec3126"

# --- Få brugerens lokation via IP ---
with st.spinner("Henter din lokation..."):
    ip_info = requests.get("https://ipapi.co/json/").json()
    lat, lon = ip_info['latitude'], ip_info['longitude']
    by = ip_info['city']

# --- Hent vejrdata og elevation ---
weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"

with st.spinner("Henter vejrdata..."):
    weather = requests.get(weather_url).json()
    elevation = requests.get(elevation_url).json()

# --- Udtræk værdier ---
temp_auto = weather["main"]["temp"]
vind_auto = weather["wind"]["speed"]
vindvinkel_auto = weather["wind"]["deg"]
højde_auto = elevation["results"][0]["elevation"]

st.success(f"Lokation: {by} ({round(lat, 2)}, {round(lon, 2)}) – {højde_auto} m.o.h.")

# --- Brugere kan justere værdier hvis ønsket ---
st.markdown("### Juster data manuelt (valgfrit)")
temp = st.slider("Temperatur (°C)", -10, 40, int(temp_auto))
vind = st.slider("Vindstyrke (m/s)", 0, 20, int(vind_auto))
vindvinkel = st.slider("Vindvinkel (°)", 0, 360, int(vindvinkel_auto), help="0° = medvind, 180° = modvind")

# --- Kølledata og beregning ---
køller = {
    "Driver": 230,
    "3-wood": 210,
    "5-iron": 170,
    "7-iron": 150,
    "9-iron": 125,
    "PW": 110,
    "SW": 90
}

def korrigeret_afstand(standard_længde, temperatur, vindstyrke, vindvinkel):
    temp_diff = temperatur - 20
    temp_faktor = 1 + 0.003 * temp_diff
    vind_faktor = np.cos(np.radians(vindvinkel)) * 0.01 * vindstyrke
    samlet_faktor = temp_faktor + vind_faktor
    return round(standard_længde * samlet_faktor, 1)

# --- Beregning ---
data = []
for kølle, længde in køller.items():
    korrigeret = korrigeret_afstand(længde, temp, vind, vindvinkel)
    data.append({
        "Kølle": kølle,
        "Normal længde (m)": længde,
        "Korrigeret længde (m)": korrigeret
    })

st.markdown("### 📊 Korrigeret Slaglængde")
st.dataframe(pd.DataFrame(data))
