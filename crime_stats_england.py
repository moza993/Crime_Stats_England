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
    url_base = "https://raw.githubusercontent.com/moza993/Crime_Stats_England/refs/heads/main/high_fidelity/"
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
    ["By constabulary & month", "All data (lower fidelity)"],
    index=0
)

# --- Cache reset button ---
if "should_rerun" not in st.session_state:
    st.session_state.should_rerun = False

clear_button = st.button("🔄 Clear Cache")
if clear_button and not st.session_state.should_rerun:
    st.cache_data.clear()
    st.session_state.should_rerun = True
    st.stop()  # Gracefully stop the script before rerunning

if st.session_state.should_rerun:
    st.session_state.should_rerun = False
    st.experimental_rerun()


# --- Load data and set filters ---
if fidelity_option == "By constabulary & month":
    constabulaires = load_constabularies()
    constabulary = st.selectbox("Select a Constabulary:", sorted(constabulaires['Constabulary'].dropna().unique()))
    map_df = load_high_fidelity_data(constabulary)
    month = st.selectbox("Select a Month:", sorted(map_df['Month'].dropna().unique()))
    crime_type = st.selectbox("Select a Crime Type:", sorted(map_df['Crime type'].dropna().unique()))

    filtered = map_df[
        (map_df['Crime type'] == crime_type) &
        (map_df['Month'] == month)
    ].sort_values(by='Count', ascending=False)

    st.markdown(f"Showing **{sum(filtered['Count'])}** `{crime_type}` crimes in `{constabulary}` for `{month}`.")

else:
    map_df = load_low_fidelity_data()
    crime_type = st.selectbox("Select a Crime Type:", sorted(map_df['Crime type'].dropna().unique()))

    filtered = map_df[
        (map_df['Crime type'] == crime_type)
    ].sort_values(by='Count', ascending=False)

    st.markdown(f"Showing **{sum(filtered['Count'])}** `{crime_type}` crimes across all constabularies for full year.")

# --- Map Creation ---
if not filtered.empty:

    if fidelity_option == "All data (lower fidelity)":

        m = folium.Map(location=[filtered['Latitude'].mean(), filtered['Longitude'].mean()],
                zoom_start=7,
                min_zoom=6,
                max_zoom=11)

        heat_data = filtered[['Latitude', 'Longitude', 'Count']].dropna().values.tolist()

        HeatMap(
            data=heat_data,
            radius=13,
            blur=15,
            max_zoom=3,
            max_val=filtered['Count'].max(),
            gradient = {
                0.0: 'navy',       # Very low density
                0.1: 'blue',
                0.3: 'cyan',
                0.4: 'lime',
                0.6: 'yellow',
                0.7: 'orange',
                0.85: 'red',
                1.0: 'maroon'       # Extreme density
            }
        ).add_to(m)

    else:

        m = folium.Map(location=[filtered['Latitude'].mean(), filtered['Longitude'].mean()],
                zoom_start=6,
                min_zoom=9)

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
