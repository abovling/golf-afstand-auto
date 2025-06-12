import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Golf – Korrigeret Slaglængde")
st.markdown("Vælg en golfklub og få dine slaglængder justeret efter lokale vindforhold.")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Klubdata inkl. St Andrews
klubber = {
    "Birkemose Golf Club": ("6000", 55.476, 9.537),
    "Langesø Golfklub": ("5462", 55.4041, 10.2215),
    "Comwell Kellers Park": ("7080", 55.355, 9.200),
    "Fredericia Golf Club": ("7000", 55.568, 9.739),
    "Golfklubben Lillebælt": ("5500", 55.507, 9.757),
    "Blommenslyst Golfklub": ("5491", 55.339, 9.292),
    "Vestfyns Golfklub": ("5620", 55.365, 9.228),
    "Faaborg Golfklub": ("5600", 55.097, 10.225),
    "Kolding Golf Club": ("6000", 55.484, 9.491),
    "Vejle Golf Club": ("7100", 55.707, 9.532),
    "Midtfyns Golfklub": ("5750", 55.274, 10.441),
    "The Old Course at St Andrews": ("KY16", 56.342, -2.796),
}

# --- Vælg golfklub via dropdown
klubnavne = list(klubber.keys())
valgt_klub = st.selectbox("Vælg golfklub:", ["Ingen valgt"] + klubnavne)

if valgt_klub != "Ingen valgt":
    postnr, lat, lon = klubber[valgt_klub]
    st.success(f"Valgt: {valgt_klub} ({postnr})")
else:
    lat, lon = None, None
    st.warning("Ingen golfklub valgt – vejrdata og højde deaktiveret.")

# --- Konverter vindretning til verdenshjørne
def grader_til_retning(deg):
    retninger = ["N", "NØ", "Ø", "SØ", "S", "SV", "V", "NV"]
    idx = int((deg + 22.5) % 360 // 45)
    return retninger[idx]

# --- Hent vejrdata og højde
if lat is not None:
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
        weather = requests.get(weather_url).json()

        elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
        elevation = requests.get(elevation_url).json()
        højde_auto = elevation["results"][0]["elevation"]

        temp_auto = weather["main"]["temp"]
        vind_auto = weather["wind"]["speed"]
        vindvinkel_auto = weather["wind"].get("deg", 0)
        vindretning_str = grader_til_retning(vindvinkel_auto)

        st.info(f"Højde: {højde_auto} m.o.h.")
        st.info(f"Vind: {vind_auto} m/s, {vindvinkel_auto}° ({vindretning_str} 🧭)")

    except:
        st.warning("Kunne ikke hente vejrdata – brug manuel input.")
        temp_auto, vind_auto, vindvinkel_auto, vindretning_str = 20, 0, 0, "Ukendt"
else:
    temp_auto, vind_auto, vindvinkel_auto, vindretning_str = 20, 0, 0, "Ukendt"

# --- Manuel justering
st.markdown("### Justér vejrdata manuelt (valgfrit)")
temp = st.slider("Temperatur (°C)", -10, 40, int(temp_auto))
vind = st.slider("Vindstyrke (m/s)", 0, 20, int(vind_auto))

# --- Køller og beregning
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

# --- Beregn
data = []
for kølle, længde in køller.items():
    korrigeret = korrigeret_afstand(længde, temp, vind, vindvinkel_auto)
    data.append({
        "Kølle": kølle,
        "Normal længde (m)": længde,
        "Korrigeret længde (m)": korrigeret
    })

st.markdown("### 📊 Korrigeret Slaglængde")
st.dataframe(pd.DataFrame(data))
