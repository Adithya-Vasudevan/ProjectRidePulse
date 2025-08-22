import math
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from utils.mock_data import create_mock_station_data, create_mock_history
from utils.plots import kpi_cards, top_stations_bar, short_term_trend_chart, utilization_hist

# Optional: enhanced badges (safe if not present)
try:
    from utils.badges import award_badge, track_page_visit
    track_page_visit("All-in-One Demo")
    award_badge("explorer")
except Exception:
    pass

st.set_page_config(page_title="All‑in‑One • RidePulse NYC (Demo)", page_icon="🧩", layout="wide")

st.title("🧩 All‑in‑One Dashboard (Demo)")
st.info("🎮 **Demo Mode**: Showcasing all features with mock data to demonstrate the complete enhanced RidePulse experience!")

# Mock data
df = create_mock_station_data()
hist = create_mock_history()

# ===== Overview =====
st.markdown("## Overview")
kc1, kc2, kc3, kc4 = st.columns(4)
kpi_cards(df, kc1, kc2, kc3, kc4)

ov_left, ov_right = st.columns([2, 1])
with ov_left:
    st.subheader("📈 Short‑term Availability Trend")
    tr = short_term_trend_chart(hist)
    st.plotly_chart(tr["fig"], use_container_width=True)

with ov_right:
    st.subheader("🏆 Top Stations (Interactive)")
    st.plotly_chart(top_stations_bar(df, n=12), use_container_width=True)
    st.caption("In live mode, these bars are clickable for drilldown!")

# ===== Stations Explorer =====
st.markdown("## Stations Explorer")
st.caption("Choose a station to see its current status and composition.")
st_left, st_right = st.columns([1, 1])

with st_left:
    station_names = sorted(df["name"].tolist())
    selected_station = st.selectbox("Station", station_names, index=0)
    
    if selected_station:
        row = df[df["name"] == selected_station].iloc[0]
        bikes = int(row["num_bikes_available"])
        docks = int(row["num_docks_available"])
        capacity = max(bikes + docks, 1)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Bikes", f"{bikes}")
        c2.metric("Docks", f"{docks}")
        c3.metric("Utilization", f"{(bikes/capacity)*100:.1f}%")
        
        # Simple composition chart
        comp = pd.DataFrame({"Type": ["Bikes", "Docks"], "Count": [bikes, docks]})
        fig_pie = px.pie(comp, values="Count", names="Type", title="Composition", hole=0.45, color_discrete_sequence=["#2563eb", "#10b981"])
        fig_pie.update_layout(margin=dict(l=10, r=10, t=60, b=10), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

with st_right:
    if selected_station:
        row = df[df["name"] == selected_station].iloc[0]
        st.subheader("Location")
        st.write({"Latitude": float(row["lat"]), "Longitude": float(row["lon"])})
        
        # Single station map
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=[{"lat": row["lat"], "lon": row["lon"], "name": row["name"]}],
            get_position="[lon, lat]",
            get_fill_color=[63, 185, 80, 200],
            get_radius=80,
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=row["lat"], longitude=row["lon"], zoom=14, pitch=30)
        tooltip = {"html": "<b>{name}</b>", "style": {"backgroundColor": "rgba(13,17,23,0.9)", "color": "white"}}
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip), use_container_width=True)

# ===== Trends =====
st.markdown("## Trends")
df_hist = hist.copy()
df_hist["ts_local"] = pd.to_datetime(df_hist["ts"]).dt.tz_convert(None)

t1, t2 = st.columns(2)
with t1:
    fig1 = px.line(df_hist, x="ts_local", y=["total_bikes", "total_docks"], title="Bikes and Docks Over Time", markers=True)
    st.plotly_chart(fig1, use_container_width=True)
with t2:
    fig2 = px.line(df_hist, x="ts_local", y="avg_percent_full", title="Average Station Fill (%)", markers=True)
    fig2.update_traces(line_color="#f59e0b")
    st.plotly_chart(fig2, use_container_width=True)

# ===== Models Lab (Mini) =====
st.markdown("## Models Lab (Mini)")
st.caption("Estimate trip duration by distance and assumed speed.")
ml1, ml2 = st.columns(2)

with ml1:
    s_names = station_names
    sA = st.selectbox("Start", s_names, key="ml_start", index=0)
    sB = st.selectbox("End", s_names, key="ml_end", index=1 if len(s_names) > 1 else 0)
    speed = st.slider("Assumed Average Speed (km/h)", 8, 25, 14)
    
    if sA and sB and sA != sB:
        a = df[df["name"] == sA].iloc[0]
        b = df[df["name"] == sB].iloc[0]
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            x = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            return R * (2 * math.atan2(math.sqrt(x), math.sqrt(1 - x)))
        
        dist_km = haversine(a["lat"], a["lon"], b["lat"], b["lon"])
        est_min = (dist_km / max(speed, 0.001)) * 60
        
        m1, m2 = st.columns(2)
        m1.metric("Distance", f"{dist_km:.2f} km")
        m2.metric("Estimated Duration", f"{est_min:.1f} min")

with ml2:
    st.info("💡 **Tip**: Midday trips often run faster than peak-hour trips due to fewer stops and lighter crossings.")

# ===== Fun Facts =====
st.markdown("## Fun Facts")
ff1, ff2, ff3 = st.columns(3)

most_bikes = df.loc[df["num_bikes_available"].idxmax(), "name"]
highest_fill = df.loc[df["percent_full"].idxmax(), "name"]
most_docks = df.loc[df["num_docks_available"].idxmax(), "name"]

ff1.metric("🏙️ Most Bikes Now", most_bikes)
ff2.metric("🥇 Highest Fill %", highest_fill)
ff3.metric("🆓 Most Docks Free", most_docks)

# Quick visualization
st.plotly_chart(utilization_hist(df), use_container_width=True)

# ===== Quiz Mini =====
st.markdown("## Quiz (Mini)")
with st.expander("🧩 Quick Citi Bike Knowledge Check"):
    st.write("**Q:** Citi Bike live data comes from which standard?")
    quiz_col1, quiz_col2, quiz_col3 = st.columns(3)
    
    with quiz_col1:
        if st.button("GBFS ✅", key="q1_correct"):
            st.success("Correct! GBFS (General Bikeshare Feed Specification)")
    with quiz_col2:
        if st.button("GTFS", key="q1_wrong1"):
            st.error("Not quite. GTFS is for transit schedules.")
    with quiz_col3:
        if st.button("OSM", key="q1_wrong2"):
            st.error("Not quite. OSM is OpenStreetMap data.")

# ===== Auto Story =====
st.markdown("## Auto Story")
top_busy = df.sort_values("percent_full", ascending=False).head(3)
story = f"📈 **Current Network Pulse**: The busiest stations right now are {', '.join(top_busy['name'].tolist()[:2])} and {top_busy['name'].iloc[2]}. "
story += f"Overall, {len(df)} stations are online with an average fill of {(df['percent_full'].mean()*100):.1f}%. "
zero_bikes = (df['num_bikes_available'] == 0).sum()
if zero_bikes > 0:
    story += f"⚠️ {zero_bikes} stations currently have zero bikes available."
else:
    story += "✅ All stations have bikes available!"
st.write(story)

# ===== Live Map Preview =====
st.markdown("## Live Map Preview")
st.caption(f"Showing {len(df)} stations on the map. Larger dots = more bikes available.")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df[["lat", "lon", "name", "num_bikes_available"]],
    get_position="[lon, lat]",
    get_fill_color="[200, 30, 0, 160]",
    get_radius="num_bikes_available * 10 + 20",
    pickable=True,
)
view_state = pdk.ViewState(latitude=40.7589, longitude=-73.9851, zoom=11, pitch=0)
tooltip = {"html": "<b>{name}</b><br>Bikes: {num_bikes_available}", "style": {"backgroundColor": "rgba(13,17,23,0.9)", "color": "white"}}
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip), use_container_width=True)

st.markdown("---")
st.success("🎯 **All-in-One Complete!** This demo showcases all the enhanced RidePulse features working together.")

# Feature summary
st.markdown("### ✨ Enhanced Features Demonstrated")
feature_cols = st.columns(2)

with feature_cols[0]:
    st.markdown("""
    **🎨 Visual Enhancements**
    - Dark theme with automatic detection
    - Improved chart layouts (no cropped titles)
    - Theme-aware CSS styling
    - Smooth animations and transitions
    """)

with feature_cols[1]:
    st.markdown("""
    **🔧 Interactive Features**
    - Click-to-drilldown bar charts
    - Enhanced hover information
    - Badge system with persistence
    - Page visit tracking
    - Private award logging
    """)