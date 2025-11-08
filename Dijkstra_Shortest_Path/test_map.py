"""Test if folium maps render in streamlit"""
import streamlit as st
from streamlit_folium import st_folium
import folium

st.title("Map Rendering Test")

# Create a simple folium map
m = folium.Map(
    location=[30.3165, 78.0322],
    zoom_start=12,
    tiles='OpenStreetMap'
)

# Add a marker
folium.Marker(
    [30.3165, 78.0322],
    popup="Test Location",
    icon=folium.Icon(color='red')
).add_to(m)

# Add a simple line
folium.PolyLine(
    locations=[
        [30.3165, 78.0322],
        [30.3255, 78.0436]
    ],
    color='red',
    weight=5,
    opacity=0.8
).add_to(m)

st.write("Map should appear below:")

# Render the map
map_data = st_folium(m, height=600, key="test_map")

st.write(f"Map data returned: {map_data is not None}")
st.write(f"Map data type: {type(map_data)}")

if map_data:
    st.write("Map data content:")
    st.json(map_data)
