import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Golf – Korrigeret Slaglængde")
st.markdown("Denne app justerer dine slaglængder baseret på **lokalt vejr og højde**.")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Lokation via IP ---
with st.spinner("Henter din lokation..."):
    try:
        ip_info = requests.get("https://ipapi.co/json/").json()
        lat, lon = ip_info['latitude'], ip_info['longitude']
        by = ip_info.get('city', 'Ukendt')
    except Exception as e:
        st.error("Kunne ikke hente lokation.")
        st.stop()

# --- Hent vejr og højde ---
weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"

with st.spinner("Henter vejrdata..."):
    try:
        weather = requests.get(weather_url).json()
        elevation = requests.get(elevation_url).json()
        
        if "main" not in weather or "wind" not in weather:
            st.error(f"Fejl fra vejr-API: {weather.get('message', 'Ukendt fejl')}")
            st.stop()

        temp_auto = weather["main"]["temp"]
        vind_auto = weather["wind"]["speed"]
        vindvinkel_auto = weather["wind"].get("deg", 0)
        højde_auto = elevation["results"][0]["elevation"]

    except Exception as e:
        st.error("Kunne ikke hente vejr- eller højdeinformation.")
        st.stop()

# --- Info ---
st.success(f"Lokation: {by} ({round(lat, 2)}, {round(lon, 2)}) – {højde_auto} m.o.h.")

# --- Manuel justering ---
st.markdown("### Juster data manuelt (valgfrit)")
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
