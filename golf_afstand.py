
import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Golfslag beregner", layout="centered")
st.title("🏌️‍♂️ Slaglængde")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Klubdata ---
baner = {
    "Danmark": {
        "Trekantsområdet": {
            "Kolding Golf Club": ("6000", 55.484, 9.491),
            "Birkemose Golf Club": ("6000", 55.476, 9.537),
            "Vejle Golf Club": ("7100", 55.707, 9.532),
            "Fredericia Golf Club": ("7000", 55.568, 9.739),
            "Comwell Kellers Park": ("7080", 55.355, 9.200),
        },
        "Fyn": {
            "Golfklubben Lillebælt": ("5500", 55.507, 9.757),
            "Blommenslyst Golfklub": ("5491", 55.339, 9.292),
            "Vestfyns Golfklub": ("5620", 55.365, 9.228),
            "Faaborg Golfklub": ("5600", 55.097, 10.225),
            "Midtfyns Golfklub": ("5750", 55.274, 10.441),
            "Langesø Golfklub": ("5462", 55.4041, 10.2215),
        },
    },
    "Skotland": {
        "St Andrews": {
            "The Old Course at St Andrews": ("KY16", 56.342, -2.796)
        }
    }
}

# --- Vindretning til verdenshjørne ---
def grader_til_retning(deg):
    retninger = ["N", "NØ", "Ø", "SØ", "S", "SV", "V", "NV"]
    idx = int((deg + 22.5) % 360 // 45)
    return retninger[idx]

# --- Brugervalg ---
land = st.radio("Vælg land:", list(baner.keys()), index=0)

områdeliste = list(baner[land].keys())
område_index = områdeliste.index("Fyn") if "Fyn" in områdeliste else 0
område = st.selectbox("Vælg område:", områdeliste, index=område_index)

klubber = baner[land][område]
klubnavne = list(klubber.keys())
klub_index = klubnavne.index("Langesø Golfklub") if "Langesø Golfklub" in klubnavne else 0
valgt_klub = st.selectbox("Vælg golfklub:", klubnavne, index=klub_index)

# --- Find lokation ---
postnr, lat, lon = klubber[valgt_klub]

# --- Hent vejr og højde ---
try:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}"
    weather = requests.get(weather_url).json()

    elevation_url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    elevation = requests.get(elevation_url).json()
    højde_auto = elevation["results"][0]["elevation"]

    temp = weather["main"]["temp"]
    vind = weather["wind"]["speed"]
    vindvinkel_auto = weather["wind"].get("deg", 0)
    vindretning_str = grader_til_retning(vindvinkel_auto)
    regner = "rain" in weather or weather.get("weather", [{}])[0].get("main") == "Rain"

except:
    st.warning("Kunne ikke hente vejrdata – standardværdier bruges.")
    temp = 20
    vind = 0
    vindvinkel_auto = 0
    højde_auto = 0
    vindretning_str = "Ukendt"
    regner = False

# --- Beregning ---
køller = {
    "7-iron": 150
}

def korrigeret_afstand(standard_længde, temperatur, vindstyrke, vindvinkel, højde, regner):
    temp_diff = temperatur - 20
    temp_faktor = 1 + 0.003 * temp_diff
    vind_faktor = np.cos(np.radians(vindvinkel)) * 0.01 * vindstyrke
    højde_faktor = 1 + 0.0001 * højde  # +1 % per 100 m højde
    regn_faktor = 0.97 if regner else 1.00  # -3 % ved regn
    samlet_faktor = temp_faktor + vind_faktor
    return round(standard_længde * samlet_faktor * højde_faktor * regn_faktor, 1)

ref_længde = køller["7-iron"]
neutral = korrigeret_afstand(ref_længde, temp, vind, vindvinkel_auto, højde_auto, regner)
modvind = korrigeret_afstand(ref_længde, temp, vind, 180, højde_auto, regner)
medvind = korrigeret_afstand(ref_længde, temp, vind, 0, højde_auto, regner)

procent_neutral = round((neutral / ref_længde) * 100, 1)
procent_modvind = round((modvind / ref_længde) * 100, 1)
procent_medvind = round((medvind / ref_længde) * 100, 1)

# --- Resultat ---
st.markdown(f"### 🏌️ Slaglængde i dag: **{procent_neutral} %**")
st.caption("(baseret på 7-jern, 150 m)")
st.text(f"Vind: {vind} m/s fra {vindretning_str} – {temp} °C – {højde_auto} m.o.h.")
st.text(f"Slaglængde i modvind: {procent_modvind} %")
st.text(f"Slaglængde i medvind: {procent_medvind} %")
if regner:
    st.info("Det regner – slaglængden er reduceret med 3 %.")
