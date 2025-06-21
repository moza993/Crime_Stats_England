import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import st_folium

url = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/main/data/constabularies.csv"
constabulaires = pd.read_csv(url)

constabulary = st.selectbox("Select a Constabulary:", sorted(constabulaires['Constabulary'].dropna().unique()))

# Dynamically load only the selected constabulary's data
url_base = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/main/data/"
filename = f"{constabulary.replace(' ', '_')}.csv"
map_df = pd.read_csv(url_base + filename)

st.set_page_config(page_title="Crime Map Viewer", layout="wide")
st.title("🗺️ Interactive Crime Map - April 2024 to 2025")

crime_type = st.selectbox("Select a Crime Type:", sorted(map_df['Crime type'].dropna().unique()))

# --- Filtering the data ---
filtered = map_df[
    (map_df['Crime type'] == crime_type) &
    (map_df['Constabulary'] == constabulary)
].sort_values(by='Count', ascending=False)

# --- Show filtered count ---
st.markdown(f"Showing **{len(filtered)}** `{crime_type}` crimes in `{constabulary}`")

# --- Generate Folium map ---
if not filtered.empty:
    m = folium.Map(location=[filtered['Latitude'].mean(), filtered['Longitude'].mean()], zoom_start=7)
    cluster = MarkerCluster().add_to(m)

    for _, row in filtered.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            tooltip=f"Crimes: {row['Count']}",
            popup=(
                f"Crime: {row['Crime type']}<br>"
                f"Date: {row['Month']}<br>"
                f"Constabulary: {row['Constabulary']}<br>"
                f"Count: {row['Count']}"
            ),
        ).add_to(cluster)

    # Show map in Streamlit
    st_data = st_folium(m, width=1000, height=600)

else:
    st.warning("No data found for the selected filters.")
