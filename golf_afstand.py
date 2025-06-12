
import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="Golfslag beregner", layout="centered")
st.title("🏌️‍♂️ Slaglængde")
st.caption("_Golfberegner af Anders Bøvling (2025)_")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Opdaterede golfområder i Danmark ---
baner = {
    "Danmark": {
        "Bornholm": {
            "Nordbornholms Golfklub": ("3770", 55.295, 14.802),
            "Bornholms Golf Klub": ("3720", 55.085, 14.774),
            "Nexø Golfklub": ("3730", 55.040, 15.123),
            "Dueodde Golfbane": ("3730", 54.982, 15.096),
        },
        "Nordjylland": {
            "HimmerLand Golf Club": ("9640", 56.799, 9.335),
            "Aalborg Golf Klub": ("9000", 57.024, 9.872),
            "Frederikshavn Golfklub": ("9900", 57.442, 10.536),
        },
        "Midt- og Vestjylland": {
            "Herning Golf Klub": ("7400", 56.142, 8.972),
            "Holstebro Golfklub": ("7500", 56.352, 8.620),
        },
        "Østjylland": {
            "Silkeborg Ry Golfklub": ("8600", 56.173, 9.563),
            "Aarhus Golf Club": ("8270", 56.097, 10.179),
        },
        "Trekantsområdet": {
            "Kolding Golf Club": ("6000", 55.484, 9.491),
            "Vejle Golf Club": ("7100", 55.707, 9.532),
            "Fredericia Golf Club": ("7000", 55.568, 9.739),
        },
        "Syd- og Sønderjylland": {
            "Haderslev Golfklub": ("6100", 55.259, 9.500),
            "Aabenraa Golfklub": ("6200", 55.044, 9.408),
        },
        "Fyn": {
            "Langesø Golfklub": ("5462", 55.4041, 10.2215),
            "Golfklubben Lillebælt": ("5500", 55.507, 9.757),
            "Faaborg Golfklub": ("5600", 55.097, 10.225),
        },
        "Sydsjælland og Møn": {
            "Næstved Golfklub": ("4700", 55.223, 11.749),
            "Falster Golfklub": ("4800", 54.764, 11.882),
        },
        "Midt- og Vestsjælland": {
            "Kalundborg Golfklub": ("4400", 55.684, 11.099),
            "Holbæk Golfklub": ("4300", 55.717, 11.697),
        },
        "Nordsjælland": {
            "Helsingør Golf Club": ("3000", 56.018, 12.561),
            "Rungsted Golf Klub": ("2960", 55.885, 12.533),
        },
        "Hovedstaden": {
            "Københavns Golf Klub": ("2840", 55.771, 12.502),
            "Dragør Golfklub": ("2791", 55.600, 12.663),
        }
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
område = st.selectbox("Vælg område:", områdeliste)

klubber = baner[land][område]
klubnavne = list(klubber.keys())
valgt_klub = st.selectbox("Vælg golfklub:", klubnavne)

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
    højde_faktor = 1 + 0.0001 * højde
    regn_faktor = 0.97 if regner else 1.00
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
