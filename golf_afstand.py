
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from supabase import create_client

supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]
supabase = create_client(supabase_url, supabase_key)

def opdater_besøg():
    supabase.table("besøg").insert(
        {"timestamp": datetime.utcnow().isoformat()}
    ).execute()
    count = supabase.table("besøg").select("*", count="exact").execute().count
    return count

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
            "Aalborg Golf Klub": ("9000", 57.024, 9.872),
            "HimmerLand Golf Club": ("9640", 56.799, 9.335),
            "Frederikshavn Golfklub": ("9900", 57.442, 10.536),
            "Hjørring Golfklub": ("9800", 57.465, 9.997),
            "Brønderslev Golfklub": ("9700", 57.271, 9.939),
            "Sæby Golfklub": ("9300", 57.338, 10.508),
            "Sindal Golfklub": ("9870", 57.449, 10.127),
            "Sebber Kloster Golfklub": ("9240", 56.880, 9.405),
            "Løgstør Golfklub": ("9670", 56.967, 9.258),
            "Hals Golfklub": ("9370", 57.002, 10.308),
            "Øland Golfklub": ("9460", 57.103, 9.294),
            "Aars Golfklub": ("9600", 56.809, 9.512),
            "Dronninglund Golfklub": ("9330", 57.176, 10.291),
            "Lemvig Golfklub": ("7620", 56.552, 8.305)
        },
        "Midt- og Vestjylland": {
            "Herning Golf Klub": ("7400", 56.142, 8.972),
            "Holstebro Golfklub": ("7500", 56.352, 8.620),
            "Struer Golfklub": ("7600", 56.492, 8.582),
            "Skive Golfklub": ("7800", 56.566, 9.017),
            "Ikast Golfklub": ("7430", 56.137, 9.170),
            "Viborg Golfklub": ("8800", 56.451, 9.401),
            "Trehøje Golfklub": ("7480", 56.246, 8.844),
            "Thisted Golfklub": ("7700", 56.955, 8.693),
            "Hvalpsund Golfklub": ("9640", 56.683, 9.023),
            "Morsø Golfklub": ("7900", 56.793, 8.862),
            "Lemvig Golfklub": ("7620", 56.552, 8.305),
            "Salling Golfklub": ("7870", 56.630, 8.962),
            "Aulum Golfklub": ("7490", 56.280, 8.756),
            "Brande Golfklub": ("7330", 55.936, 9.128)
        },
        "Østjylland": {
            "Lübker Golf Resort": ("8581", 56.415, 10.695),
            "Silkeborg Ry Golfklub": ("8600", 56.173, 9.563),
            "Aarhus Golf Club": ("8270", 56.097, 10.179),
            "Odder Golfklub": ("8300", 55.973, 10.125),
            "Ebeltoft Golfklub": ("8400", 56.199, 10.684),
            "Grenaa Golfklub": ("8500", 56.422, 10.876),
            "Hammel Golfklub": ("8450", 56.285, 9.865),
            "Samsø Golfklub": ("8305", 55.911, 10.601),
            "Djurs Golfklub": ("8585", 56.460, 10.717),
            "Kalø Golfklub": ("8410", 56.301, 10.527),
            "Lyngbygaard Golf": ("8220", 56.131, 10.021),
            "Randers Golfklub": ("8920", 56.420, 10.093),
            "Favrskov Golfklub": ("8370", 56.276, 9.969),
            "Skanderborg Golfklub": ("8660", 56.051, 9.938),
            "Hedensted Golfklub": ("8722", 55.788, 9.714),
            "Horsens Golfklub": ("8700", 55.845, 9.868)
        },
        "Trekantsområdet": {
            "Kolding Golf Club": ("6000", 55.484, 9.491),
            "Vejle Golf Club": ("7100", 55.707, 9.532),
            "Fredericia Golf Club": ("7000", 55.568, 9.739),
            "Birkemose Golf Club": ("6000", 55.462, 9.463),
            "Jelling Golfklub": ("7300", 55.747, 9.417),
            "Give Golfklub": ("7323", 55.847, 9.331),
            "Hedensted Golfklub": ("8722", 55.788, 9.714),
            "Vandel Golfklub": ("7184", 55.704, 9.186),
            "Vejle Golfbane Øst": ("7120", 55.657, 9.576),
            "Middelfart Golfklub": ("5500", 55.492, 9.736),
            "Tørring Golfklub": ("7160", 55.851, 9.484),
            "Seest Golfklub": ("6000", 55.472, 9.478),
            "Brande Golfklub": ("7330", 55.936, 9.128),
            "Egtved Golfklub": ("6040", 55.617, 9.421)
        },
        "Syd- og Sønderjylland": {
    "Haderslev Golfklub": ("6100", 55.259, 9.500),
    "Aabenraa Golfklub": ("6200", 55.044, 9.408),
    "Tønder Golfklub": ("6270", 54.936, 8.869),
    "Sønderjyllands Golfklub": ("6510", 55.080, 9.278),
    "Vejen Golfklub": ("6600", 55.489, 9.136),
    "Toftlund Golfklub": ("6520", 55.149, 9.092),
    "Rødding Golfklub": ("6630", 55.385, 9.124),
    "Gråsten Golfklub": ("6300", 54.919, 9.618),
    "Benniksgaard Golf Klub": ("6340", 54.893, 9.529),
    "Skærbæk Mølle Golfklub": ("6780", 55.026, 8.771),
    "Arrild Golfklub": ("6510", 55.127, 9.008),
    "Nordborg Golfklub": ("6430", 55.059, 9.782),
    "Blåvandshuk Golfklub": ("6840", 55.562, 8.147),
    "Esbjerg Golfklub": ("6710", 55.471, 8.389)
},
        "Fyn": {
    "Langesø Golfklub": ("5462", 55.403, 10.204),
    "Odense Eventyr Golf": ("5220", 55.368, 10.373),
    "Odense Golfklub": ("5491", 55.396, 10.328),
    "Sct. Knuds Golfklub Nyborg": ("5800", 55.316, 10.787),
    "Midtfyns Golfklub": ("5750", 55.213, 10.436),
    "Faaborg Golfklub": ("5600", 55.088, 10.205),
    "Langelands Golfklub": ("5953", 54.891, 10.775),
    "Great Northern": ("5300", 55.314, 10.800),
    "Vestfyns Golfklub": ("5610", 55.386, 9.983),
    "H.C. Andersen Golf": ("5771", 55.162, 10.367),
    "Birkemose Golf Club": ("6000", 55.462, 9.463),
    "Middelfart Golfklub": ("5500", 55.492, 9.736),
    "Ærø Golf Klub": ("5970", 54.846, 10.406),
    "Svendborg Golf Klub": ("5700", 55.030, 10.599)
},
        "Sjælland og Øerne": {
    "Royal Golf Club": ("2300", 55.625, 12.594),
    "Køge Golf Klub": ("4600", 55.473, 12.158),
    "Himmerødgård Golfklub": ("4000", 55.635, 12.100),
    "Roskilde Golfklub": ("4000", 55.629, 12.097),
    "Skjoldenæsholm Golfklub": ("4174", 55.542, 11.806),
    "Sorø Golfklub": ("4180", 55.438, 11.561),
    "Trelleborg Golfklub Slagelse": ("4200", 55.406, 11.358),
    "Holbæk Golfklub": ("4300", 55.695, 11.704),
    "Kalundborg Golfklub": ("4400", 55.676, 11.068),
    "Odsherred Golfklub": ("4500", 55.872, 11.511),
    "Asserbo Golf Club": ("3300", 55.993, 12.036),
    "Næstved Golfklub": ("4700", 55.200, 11.755),
    "Falster Golfklub": ("4800", 54.780, 11.891),
    "Maribo Sø Golfklub": ("4930", 54.767, 11.491),
    "Storstrømmen Golfklub": ("4800", 54.769, 11.848),
    "Møn Golfklub": ("4780", 54.991, 12.216),
    "Lolland Golfklub": ("4900", 54.767, 11.260),
    "Sydsjællands Golfklub": ("4760", 55.055, 11.997)
},
    },
    
}

# --- Vindretning til verdenshjørne ---
def grader_til_retning(deg):
    retninger = ["N", "NØ", "Ø", "SØ", "S", "SV", "V", "NV"]
    idx = int((deg + 22.5) % 360 // 45)
    return retninger[idx]

# --- Brugervalg ---
land = st.radio("Vælg land:", list(baner.keys()), index=0)

områdeliste = list(baner[land].keys())
område = st.selectbox("Vælg område:", områdeliste, index=områdeliste.index("Fyn"))

klubber = baner[land][område]
klubnavne = list(klubber.keys())



standard_klub = "Langesø Golfklub"
if klubnavne:
    if standard_klub in klubnavne:
        index = klubnavne.index(standard_klub)
    else:
        index = 0  # vælg første klub i listen
    valgt_klub = st.selectbox("Vælg golfklub:", klubnavne, index=index)
else:
    valgt_klub = None
    st.warning("Der er ingen golfklubber i det valgte område.")

# --- Favoritfunktion ---

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
neutral = korrigeret_afstand(ref_længde, temp, 0, 0, højde_auto, regner)
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

from datetime import datetime
nu = datetime.now().strftime("%d-%m-%Y kl. %H:%M")
st.markdown(f"---\n*Data hentet: {nu}*")

try:
    antal = opdater_besøg()
    st.markdown(f"👥 Antal besøg: **{antal}**")
except Exception as e:
    st.warning(f"Besøgs-tæller fejl: {e}")
