from turtle import bgcolor
from typing import Any
from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

img = Image.open("img.png")
st.set_page_config(page_title="Overview of Motor Vehicle Collision", page_icon=img,layout="wide")
st.title("Motor Vehicle Collisions in NYC!")
st.markdown("A streamlit dashboard that can be used to analyze Motor Vehicle Collisions in NYC!💥🚗 ")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv("dataset.csv",nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE' , 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase , axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data

data = load_data(100000)
original_data = data

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of Persons Injured in Vehicle Collisions", 0, 20)
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/dark-v9",
    initial_view_state= {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom" : 9,
        "pitch": 50,


    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"),
        get_position=['longitude' , 'latitude'],
        radius = 75,
        extruded=False,
        pickable=False,
        elevation_scale=4,
        elevation_range=[0,1000],

        ),
    ],
))

st.header("How many Collisions occur during a given time of day?")
hour = st.slider("Hour to look at", 0,23)
data = data[data['date/time'].dt.hour== hour]

st.markdown("Vehicle Collisions between %i:00 and %i:00" % (hour ,(hour + 1) % 24))
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state= {
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom" : 10,
        "pitch": 55,


    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data = data[['date/time', 'latitude', 'longitude']],
        get_position=['longitude' , 'latitude'],
        radius = 100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0,1000],

        ),
    ],
))

st.subheader("Breakdown by Minute between %i:00 and %i:00" % (hour , (hour+1) % 24))
filtered = data[
    (data['date/time'].dt.hour>= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x="minute", y="crashes", hover_data=['minute', 'crashes'], height=500)
st.write(fig)

st.header("Top 5 Dangerous streets in NYC according to type of people!")
select = st.selectbox("Affected type of people", ['Pedestrians', 'Cyclists', "Motorists"])

if select == "Pedestrians" :
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name', "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how='any')[0:5])

elif select == "Cyclists" :
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how='any')[0:5])

else :
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name', "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how='any')[0:5])


if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)
