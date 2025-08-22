import streamlit as st
import pandas as pd
import plotly.express as px
from utils.gbfs import merged_station_frame, get_snapshot_history
from utils.plots import top_stations_bar
from utils.badges import award_badge

st.set_page_config(page_title="Story Builder • RidePulse NYC", page_icon="📖", layout="wide")
award_badge("storyteller")

st.title("📖 Story Builder — Auto Narrative")

df = merged_station_frame()
hist = get_snapshot_history()

st.markdown("### Story 1: The Race to Rebalance")
top_full = df.sort_values("percent_full", ascending=False).head(5)
st.write("Stations nearing capacity often need quick rebalancing. Here are the top 5 at risk right now.")
st.dataframe(top_full[["name","percent_full","num_bikes_available","num_docks_available"]]
             .assign(**{"percent_full": (top_full["percent_full"]*100).round(1)}),
             use_container_width=True, height=280)

st.markdown("### Story 2: Who’s Winning the Bike Count?")
st.plotly_chart(top_stations_bar(df, n=12), use_container_width=True)

st.markdown("### Story 3: The Pulse of the Network")
if not (isinstance(hist, list) or len(hist) < 2):
    st.info("Building up live snapshots for time-series stories. Check back soon!")
else:
    h = hist.copy()
    h["ts_local"] = pd.to_datetime(h["ts"]).dt.tz_convert(None)
    fig = px.area(h, x="ts_local", y="total_bikes", title="Total Bikes Over Recent Time", markers=False)
    st.plotly_chart(fig, use_container_width=True)

st.success("Refresh for new live stories — perfect for judges and demos.")