import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import st_folium

# --- Cached functions ---
@st.cache_data
def load_constabularies():
    url = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/refs/heads/main/constabularies.csv"
    return pd.read_csv(url)

@st.cache_data
def load_map_data(selected_constabulary):
    url_base = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/main/split_data/"
    filename = "('"+f"{constabulary.replace(' ', '_')}"+"'%2C).csv"
    return pd.read_csv(url_base + filename)

# --- App layout ---
st.set_page_config(page_title="Crime Map Viewer", layout="wide")
st.title("🗺️ Interactive Crime Map - April 2024 to 2025")

# --- Load and select constabulary ---
constabulaires = load_constabularies()
constabulary = st.selectbox("Select a Constabulary:", sorted(constabulaires['Constabulary'].dropna().unique()))

# --- Load selected data only once ---
map_df = load_map_data(constabulary)

# --- Filters ---
crime_type = st.selectbox("Select a Crime Type:", sorted(map_df['Crime type'].dropna().unique()))
month = st.selectbox("Select a Month:", sorted(map_df['Month'].dropna().unique()))

# --- Filtering the data ---
filtered = map_df[
    (map_df['Crime type'] == crime_type) &
    (map_df['Month'] == month)
].sort_values(by='Count', ascending=False)

# --- Show filtered count ---
st.markdown(f"Showing **{len(filtered)}** `{crime_type}` crimes in `{constabulary}` for `{month}`.")

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
                f"Constabulary: {row['Constabulary']}<br>"
                f"Crimes: {row['Count']}"
            ),
        ).add_to(cluster)

    st_data = st_folium(m, width=1000, height=600)
else:
    st.warning("No data found for the selected filters.")
