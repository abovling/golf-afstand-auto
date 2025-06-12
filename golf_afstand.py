import streamlit as st
import pandas as pd
import numpy as np
import requests

st.title("Golf – Korrigeret Slaglængde")
st.markdown("Vælg en golfklub og se dine slaglængder justeret for lokale vindforhold")

# --- API-nøgle ---
WEATHER_API_KEY = "76a93862c3136e24c75df4db4cb236a4"

# --- Klubdata inkl. St Andrews ---
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
    "The Old Course at St Andrews": ("KY16", 56.342, -2.796),
}

# --- Vælg én klub (radio i to kolonner) ---
col1, col2 = st.columns(2)
navne = list(klubber.keys())
valgt = None
with col1:
    valgt = st.radio("Vælg klub:", navne[:6], index=-1)
with col2:
    valgt = st.radio(" ", navne[6:], index=-1, key="rad2") or valgt

if valgt:
    postnr, lat, lon = klubber[valgt]
    st.success(f"Valgt: {valgt} ({postnr})")
else:
    st.warning("Ingen klub valgt – manuel input for vind anvendes.")
    lat, lon = None, None

def grader_til_retning(deg):
    ret = ["N","NØ","Ø","SØ","S","SV","V","NV"]
    return ret[int((deg + 22.5) % 360 // 45)]

# --- Hent vejr hvis klub valgt ---
if lat:
    try:
        w = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}").json()
        elev = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}").json()
        højde = elev["results"][0]["elevation"]
        temp_auto = w["main"]["temp"]
        vind_auto = w["wind"]["speed"]
        deg = w["wind"].get("deg",0)
        ret = grader_til_retning(deg)
        comp = f"🧭 {ret}"
        st.info(f"Højde: {højde} m.o.h.")
        st.info(f"Vind: {vind_auto} m/s, {deg}° {comp}")
    except:
        st.warning("Fejl ved vejrdata. Brug manuel input.")
        temp_auto, vind_auto, deg, comp = 20, 0, 0, ""
else:
    temp_auto, vind_auto, deg, comp = 20, 0, 0, ""

# --- Brugervalgt input ---
st.markdown("### Justér efter behov")
temp = st.slider("Temperatur (°C)", -10, 40, int(temp_auto))
vind = st.slider("Vindstyrke (m/s)", 0, 20, int(vind_auto))

# --- Beregning ---
def korr(stand, t, v, d):
    tf = 1 + 0.003*(t-20)
    vf = np.cos(np.radians(d))*0.01*v
    return round(stand*(tf+vf),1)

køller = {"Driver":230,"3-wood":210,"7-iron":150}
rows=[]
for klub, stand in køller.items():
    rows.append({"Kølle":klub,"Normal":stand,"Beregn":korr(stand,temp,vind,deg)})
st.dataframe(pd.DataFrame(rows))
