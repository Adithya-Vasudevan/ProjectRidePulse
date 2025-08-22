import streamlit as st
import plotly.graph_objects as go
from utils.gbfs import merged_station_frame, get_snapshot_history
from utils.plots import kpi_cards, top_stations_bar, short_term_trend_chart, utilization_hist
from utils.badges import award_badge

st.set_page_config(page_title="Overview • RidePulse NYC", page_icon="📊", layout="wide")
award_badge("explorer")

st.title("📊 Overview")
df = merged_station_frame()

# KPIs
c1, c2, c3, c4 = st.columns(4)
kpi_cards(df, c1, c2, c3, c4)

# Animated gauge for Avg Fill
avg_fill = float(df["percent_full"].mean() * 100) if len(df) else 0.0
gcol, _ = st.columns([1,3])
with gcol:
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_fill,
        title={'text': "Avg Station Fill (%)"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "#2563eb"},
               'steps': [
                   {'range': [0, 33], 'color': '#ecfeff'},
                   {'range': [33, 66], 'color': '#cffafe'},
                   {'range': [66, 100], 'color': '#bae6fd'}]}
    ))
    gauge.update_layout(height=220, margin=dict(l=10,r=10,t=30,b=10))
    st.plotly_chart(gauge, use_container_width=True)

st.markdown("### 🔎 Quick Insights")
left, right = st.columns([2, 1])
with left:
    hist = get_snapshot_history()
    if isinstance(hist, list) or len(hist) < 2:
        st.info("Collecting snapshots. Trends will appear shortly.")
    else:
        trend_obj = short_term_trend_chart(hist)
        st.plotly_chart(trend_obj["fig"], use_container_width=True)

with right:
    st.plotly_chart(top_stations_bar(df, n=12), use_container_width=True)

st.markdown("### 🧭 Distribution")
st.plotly_chart(utilization_hist(df), use_container_width=True)

st.markdown("#### ✨ Story beats (auto-generated)")
top_full = df.sort_values("percent_full", ascending=False).head(1)
top_empty = df.sort_values("num_bikes_available", ascending=True).head(1)
if not top_full.empty:
    st.write(f"• Nearing capacity: {top_full.iloc[0]['name']} ({top_full.iloc[0]['percent_full']*100:.1f}% full).")
if not top_empty.empty:
    st.write(f"• Low bikes: {top_empty.iloc[0]['name']} ({top_empty.iloc[0]['num_bikes_available']} bikes).")
st.success("Use the sidebar to dive into Stations, Trends, Models Lab, Fun Facts, Quiz, Story Builder, and the Live Map.")