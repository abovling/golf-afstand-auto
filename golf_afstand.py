import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Golf – Korrigeret Slaglængde")
st.markdown("Vælg en golfklub og se dine slaglængder justeret for vejr og højde over havet.")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Klubdata: navn → (postnr, lat, lon)
klubber = {
    "Kolding Golf Club": ("6000", 55.484, 9.491),
    "Birkemose Golf Club": ("6000", 55.476, 9.537),
    "Vejle Golf Club": ("7100", 55.707, 9.532),
    "Comwell Kellers Park": ("7080", 55.355, 9.200),
    "Fredericia Golf Club": ("7000", 55.568, 9.739),
    "Golfklubben Lillebælt": ("5500", 55.507, 9.757),
    "Blommenslyst Golfklub": ("5491", 55.339, 9.292),
    "Vestfyns Golfklub": ("5620", 55.365, 9.228),
    "Faaborg Golfklub": ("5600", 55.097, 10.225),
    "Midtfyns Golfklub": ("5750", 55.274, 10.441),
}

# --- Vælg klub via checkbox
st.markdown("### Vælg én golfklub:")
valgte = [navn for navn in klubber if st.checkbox(navn)]

if valgte:
    valgt_klub = valgte[0]
    postnr, lat, lon = klubber[valgt_klub]
    st.success(f"Valgt: {valgt_klub} ({postnr})")
else:
    st.warning("Ingen klub valgt – standardplacering bruges.")
    valgt_klub = "Standardplacering"
    postnr, lat, lon = "0000", 55.0, 10.0

# --- Forsøg at hente vejr og højde
try:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
    weather = requests.get(weather_url).json()

    elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    elevation = requests.get(elevation_url).json()
    højde_auto = elevation["results"][0]["elevation"]

    temp_auto = weather["main"]["temp"]
    vind_auto = weather["wind"]["speed"]
    vindvinkel_auto = weather["wind"].get("deg", 0)
    st.success(f"Højde: {højde_auto} m.o.h.")

except Exception:
    st.warning("Kunne ikke hente vejrdata – du kan selv vælge nedenfor.")
    temp_auto = 20
    vind_auto = 0
    vindvinkel_auto = 0
    højde_auto = "Ukendt"

# --- Brugervalgt justering
st.markdown("### Juster data manuelt (valgfrit)")
temp = st.slider("Temperatur (°C)", -10, 40, int(temp_auto))
vind = st.slider("Vindstyrke (m/s)", 0, 20, int(vind_auto))
vindvinkel = st.slider("Vindvinkel (°)", 0, 360, int(vindvinkel_auto), help="0° = medvind, 180° = modvind")

# --- Kølledata og beregning
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

# --- Beregn resultater
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
