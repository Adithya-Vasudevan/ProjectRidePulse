import math
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk

from utils.gbfs import merged_station_frame, get_snapshot_history
from utils.plots import kpi_cards, top_stations_bar, short_term_trend_chart, utilization_hist

# Optional: enhanced badges (safe if not present)
try:
    from utils.badges import award_badge, track_page_visit  # type: ignore
    track_page_visit("All-in-One")
    award_badge("explorer")
except Exception:
    pass

st.set_page_config(page_title="All‑in‑One • RidePulse NYC", page_icon="🧩", layout="wide")

st.title("🧩 All‑in‑One Dashboard")
st.caption("A single page that brings together key insights, interactions, models, and the live map.")

# Data
df = merged_station_frame()
hist = get_snapshot_history()

# ===== Overview =====
st.markdown("## Overview")
kc1, kc2, kc3, kc4 = st.columns(4)
kpi_cards(df, kc1, kc2, kc3, kc4)

ov_left, ov_right = st.columns([2, 1])
with ov_left:
    st.subheader("📈 Short‑term Availability Trend")
    if isinstance(hist, list) or len(hist) < 2:
        st.info("Collecting snapshots. Come back in a minute for trends.")
    else:
        tr = short_term_trend_chart(hist)
        st.plotly_chart(tr["fig"], use_container_width=True)
    try:
        st.page_link("app.py", label="Open full Overview →", icon="🏠")
    except Exception:
        pass

with ov_right:
    st.subheader("🏆 Top Stations (Live)")
    st.plotly_chart(top_stations_bar(df, n=12), use_container_width=True)

# ===== Stations Explorer =====
st.markdown("## Stations Explorer")
st.caption("Choose a station to see its current status and composition.")
st_left, st_right = st.columns([1, 1])

with st_left:
    station_names = sorted(df["name"].dropna().unique().tolist()) if "name" in df else []
    selected_station = st.selectbox("Station", station_names, index=0 if station_names else None, placeholder="Select a station")
    if selected_station:
        row = df[df["name"] == selected_station].head(1).iloc[0]
        bikes = int(row.get("num_bikes_available", 0))
        docks = int(row.get("num_docks_available", 0))
        capacity = max(bikes + docks, 1)
        c1, c2, c3 = st.columns(3)
        c1.metric("Bikes", f"{bikes}")
        c2.metric("Docks", f"{docks}")
        c3.metric("Utilization", f"{(bikes/capacity)*100:.1f}%")
        st.caption(f"Last update (provider time): {row.get('last_reported', '')}")
        # Simple composition chart
        comp = pd.DataFrame({"Type": ["Bikes", "Docks"], "Count": [bikes, docks]})
        fig_pie = px.pie(comp, values="Count", names="Type", title="Composition", hole=0.45, color_discrete_sequence=["#2563eb", "#10b981"])
        fig_pie.update_layout(margin=dict(l=10, r=10, t=60, b=10), height=300)
        st.plotly_chart(fig_pie, use_container_width=True)

with st_right:
    if selected_station:
        row = df[df["name"] == selected_station].head(1).iloc[0]
        st.subheader("Location")
        st.write({"Latitude": float(row.get("lat", 0)), "Longitude": float(row.get("lon", 0))})
        if pd.notna(row.get("lat")) and pd.notna(row.get("lon")):
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
    try:
        st.page_link("pages/01_Stations.py", label="Open full Stations →", icon="🏙️")
    except Exception:
        pass

# ===== Trends =====
st.markdown("## Trends")
if isinstance(hist, list) or len(hist) < 5:
    st.info("Collecting snapshot history. Come back in a few minutes to see richer trends.")
else:
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
try:
    st.page_link("pages/03_Trends.py", label="Open full Trends →", icon="📈")
except Exception:
    pass

# ===== Models Lab (Mini) =====
st.markdown("## Models Lab (Mini)")
st.caption("Estimate trip duration by distance and assumed speed. For full models, open the Models Lab page.")
ml1, ml2 = st.columns(2)

with ml1:
    s_names = station_names
    sA = st.selectbox("Start", s_names, key="ml_start", index=0 if s_names else None)
    sB = st.selectbox("End", s_names, key="ml_end", index=min(1, len(s_names)-1) if s_names else None)
    speed = st.slider("Assumed Average Speed (km/h)", 8, 25, 14)
    if sA and sB:
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
    st.info("Did you know? Midday trips often run faster than peak-hour trips due to fewer stops and lighter crossings.")
try:
    st.page_link("pages/04_Models_Lab.py", label="Open full Models Lab →", icon="🔮")
except Exception:
    pass

# ===== Fun Facts =====
st.markdown("## Fun Facts")
ff1, ff2, ff3 = st.columns(3)
if len(df) > 0:
    try:
        most_bikes = df.loc[df["num_bikes_available"].idxmax(), "name"]
        highest_fill = df.loc[df["percent_full"].idxmax(), "name"]
        most_docks = df.loc[df["num_docks_available"].idxmax(), "name"]
        ff1.metric("🏙️ Most Bikes Now", most_bikes)
        ff2.metric("🥇 Highest Fill %", highest_fill)
        ff3.metric("🆓 Most Docks Free", most_docks)
    except Exception:
        ff1.info("Data loading...")
        ff2.info("Data loading...")
        ff3.info("Data loading...")
    
    # Quick visualization
    st.plotly_chart(utilization_hist(df), use_container_width=True)
try:
    st.page_link("pages/05_Fun_Facts.py", label="Open full Fun Facts →", icon="🎉")
except Exception:
    pass

# ===== Quiz Mini =====
st.markdown("## Quiz (Mini)")
with st.expander("🧩 Quick Citi Bike Knowledge Check"):
    st.write("**Q:** Citi Bike live data comes from which standard?")
    if st.button("GBFS ✅", key="q1_correct"):
        st.success("Correct! GBFS (General Bikeshare Feed Specification)")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("GTFS", key="q1_wrong1"):
            st.error("Not quite. GTFS is for transit schedules.")
    with col2:
        if st.button("OSM", key="q1_wrong2"):
            st.error("Not quite. OSM is OpenStreetMap data.")
try:
    st.page_link("pages/06_Quiz.py", label="Take full Quiz →", icon="🧠")
except Exception:
    pass

# ===== Story Builder (Mini) =====
st.markdown("## Auto Story")
if len(df) > 0:
    try:
        top_busy = df.sort_values("percent_full", ascending=False).head(3)
        story = f"📈 **Current Network Pulse**: The busiest stations right now are {', '.join(top_busy['name'].tolist()[:2])} and {top_busy['name'].iloc[2]}. "
        story += f"Overall, {len(df)} stations are online with an average fill of {(df['percent_full'].mean()*100):.1f}%. "
        zero_bikes = (df['num_bikes_available'] == 0).sum()
        if zero_bikes > 0:
            story += f"⚠️ {zero_bikes} stations currently have zero bikes available."
        else:
            story += "✅ All stations have bikes available!"
        st.write(story)
    except Exception:
        st.info("Generating story from live data...")
try:
    st.page_link("pages/07_Story_Builder.py", label="Open Story Builder →", icon="📖")
except Exception:
    pass

# ===== Live Map (Mini Preview) =====
st.markdown("## Live Map Preview")
if len(df) > 0 and "lat" in df.columns and "lon" in df.columns:
    # Simple scatter of all stations
    map_df = df[["lat", "lon", "name", "num_bikes_available"]].dropna()
    if len(map_df) > 0:
        st.caption(f"Showing {len(map_df)} stations on the map. Larger dots = more bikes available.")
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position="[lon, lat]",
            get_fill_color="[200, 30, 0, 160]",
            get_radius="num_bikes_available * 10 + 20",
            pickable=True,
        )
        view_state = pdk.ViewState(latitude=40.7589, longitude=-73.9851, zoom=11, pitch=0)
        tooltip = {"html": "<b>{name}</b><br>Bikes: {num_bikes_available}", "style": {"backgroundColor": "rgba(13,17,23,0.9)", "color": "white"}}
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip), use_container_width=True)
else:
    st.info("Map preview will appear when station data loads.")
try:
    st.page_link("pages/08_Live_Map.py", label="Open full Live Map →", icon="🗺️")
except Exception:
    pass

st.markdown("---")
st.success("🎯 **All-in-One Complete!** Use the sidebar to dive deeper into each section.")