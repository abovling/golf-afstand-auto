import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Golf – Korrigeret Slaglængde")
st.markdown("Denne app justerer dine slaglængder baseret på **lokalt vejr og højde** – automatisk, hvis muligt.")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Lokation via IP ---
with st.spinner("Henter din lokation..."):
    try:
        ip_info = requests.get("https://ipapi.co/json/").json()
        lat, lon = ip_info['latitude'], ip_info['longitude']
        by = ip_info.get('city', 'Ukendt')
    except Exception:
        lat, lon = 55.0, 10.0
        by = "Ukendt"

# --- Forsøg at hente vejr og højde ---
try:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
    weather = requests.get(weather_url).json()

    elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    elevation = requests.get(elevation_url).json()
    højde_auto = elevation["results"][0]["elevation"]

    temp_auto = weather["main"]["temp"]
    vind_auto = weather["wind"]["speed"]
    vindvinkel_auto = weather["wind"].get("deg", 0)

    auto_data = True

except Exception as e:
    auto_data = False
    st.warning("Automatisk vejrdata kunne ikke hentes – du kan indtaste det manuelt nedenfor.")
    temp_auto = 20
    vind_auto = 0
    vindvinkel_auto = 0
    højde_auto = "Ukendt"

# --- Info ---
st.success(f"Lokation: {by} ({round(lat, 2)}, {round(lon, 2)}) – {højde_auto} m.o.h.")
st.markdown("### Juster data manuelt (eller behold de foreslåede)")

# --- Input
temp = st.slider("Temperatur (°C)", -10, 40, int(temp_auto))
vind = st.slider("Vindstyrke (m/s)", 0, 20, int(vind_auto))
vindvinkel = st.slider("Vindvinkel (°)", 0, 360, int(vindvinkel_auto), help="0° = medvind, 180° = modvind")

# --- Køller og beregning ---
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
