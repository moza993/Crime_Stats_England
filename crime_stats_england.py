import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import streamlit as st
from streamlit_folium import st_folium

# --- Cached data loading ---
@st.cache_data
def load_constabularies():
    url = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/refs/heads/main/constabularies.csv"
    return pd.read_csv(url)

@st.cache_data
def load_high_fidelity_data(selected_constabulary):
    url_base = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/main/split_data/"
    filename = "('"+f"{constabulary.replace(' ', '_')}"+"'%2C).csv"

    return pd.read_csv(url_base + filename)

@st.cache_data
def load_low_fidelity_data():
    url = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/refs/heads/main/low_fidelity/low_fidelity_data.csv"
    return pd.read_csv(url)

# --- App Layout ---
st.set_page_config(page_title="Crime Map Viewer", layout="wide")
st.title("🗺️ Interactive Crime Map - April 2024 to 2025")

# --- Fidelity Toggle ---
fidelity_option = st.radio(
    "Select data fidelity:",
    ["High fidelity (per constabulary/month)", "Low fidelity (all data)"],
    index=0
)

# --- Cache reset button ---
if st.button("🔄 Clear Cache"):
    st.cache_data.clear()
    st.experimental_rerun()

# --- Load data and set filters ---
if fidelity_option == "High fidelity (per constabulary/month)":
    constabulaires = load_constabularies()
    constabulary = st.selectbox("Select a Constabulary:", sorted(constabulaires['Constabulary'].dropna().unique()))
    map_df = load_high_fidelity_data(constabulary)
else:
    map_df = load_low_fidelity_data()
    constabulary = st.selectbox("Filter by Constabulary:", sorted(map_df['Constabulary'].dropna().unique()))

crime_type = st.selectbox("Select a Crime Type:", sorted(map_df['Crime type'].dropna().unique()))
month = st.selectbox("Select a Month:", sorted(map_df['Month'].dropna().unique()))

# --- Filtering ---
filtered = map_df[
    (map_df['Crime type'] == crime_type) &
    (map_df['Constabulary'] == constabulary) &
    (map_df['Month'] == month)
].sort_values(by='Count', ascending=False)

st.markdown(f"Showing **{len(filtered)}** `{crime_type}` crimes in `{constabulary}` for `{month}`.")

# --- Map Creation ---
if not filtered.empty:
    m = folium.Map(location=[filtered['Latitude'].mean(), filtered['Longitude'].mean()], zoom_start=7)

    if fidelity_option == "Low fidelity (all data)":
        heat_data = filtered[['Latitude', 'Longitude']].dropna().values.tolist()
        HeatMap(heat_data).add_to(m)
    else:
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
