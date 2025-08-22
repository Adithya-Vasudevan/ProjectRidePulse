import streamlit as st
from utils.gbfs import merged_station_frame
from utils.models import classify_station_traffic
from utils.badges import award_badge

st.set_page_config(page_title="Stations • RidePulse NYC", page_icon="📍", layout="wide")
award_badge("station_sage")

st.title("📍 Stations Explorer")
df = merged_station_frame().copy()

# Classification labels
labels = classify_station_traffic(df)
df["traffic"] = labels if labels else "Medium"

# Search / filters
qcol, f1, f2 = st.columns([2,1,1])
query = qcol.text_input("Search by station name", "")
traffic_filter = f1.multiselect("Traffic Level", options=sorted(df["traffic"].astype(str).unique()), default=sorted(df["traffic"].astype(str).unique()))
min_bikes = f2.slider("Min available bikes", 0, int(df["num_bikes_available"].max()), 0)

filtered = df[
    df["traffic"].astype(str).isin(traffic_filter)
    & df["num_bikes_available"].ge(min_bikes)
    & df["name"].str.contains(query, case=False, na=False)
]

st.caption(f"Showing {len(filtered)} of {len(df)} stations")

st.dataframe(
    filtered[["name","num_bikes_available","num_docks_available","percent_full","traffic","capacity"]]
    .rename(columns={
        "name":"Station",
        "num_bikes_available":"🚲 Bikes",
        "num_docks_available":"🅿️ Docks",
        "percent_full":"% Full",
        "traffic":"Traffic",
        "capacity":"Capacity"
    }).assign(**{"% Full": (filtered["percent_full"]*100).round(1)}),
    use_container_width=True,
    height=520
)