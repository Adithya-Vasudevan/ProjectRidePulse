import streamlit as st
from datetime import datetime
from streamlit_plotly_events import plotly_events  # NEW: for click interactions
from utils.gbfs import merged_station_frame, record_snapshot_if_due, get_snapshot_history
from utils.plots import kpi_cards, top_stations_bar, short_term_trend_chart, station_utilization_gauge  # UPDATED
from utils.helpers import human_time
from utils.ui import show_lottie
from utils.badges import init_badges, render_badges, track_page_visit  # UPDATED
from utils.theme import inject_css

st.set_page_config(
    page_title="RidePulse NYC — Live Bike Intelligence",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS animations/theme
inject_css()

# Sidebar brand + badges
with st.sidebar:
    st.title("🚲 RidePulse NYC")
    st.caption("Live Bike Intelligence • Citi Bike GBFS")
    render_badges()
    st.markdown("---")
    refresh = st.button("🔄 Refresh Now")
    st.caption("Use the sidebar Pages to explore everything.")

# Initialize achievements system
init_badges()
track_page_visit("Overview")  # NEW: Counts toward 'Explorer'

# Animated header
col_a, col_b = st.columns([1, 3])
with col_a:
    show_lottie("https://assets8.lottiefiles.com/packages/lf20_u4yrau.json", height=120)
with col_b:
    st.markdown("## 🚀 RidePulse NYC — Live Bike Intelligence")
    st.write("Live data, interactive models, animated visuals, and maps designed to win 👑.")

# Fetch + record snapshot
df = merged_station_frame(force=refresh)
record_snapshot_if_due(df)

# KPIs
c1, c2, c3, c4 = st.columns(4)
kpi_cards(df, c1, c2, c3, c4)

# Highlights
st.markdown("### ⚡ Highlights")
left, right = st.columns([2, 1])

with left:
    st.subheader("📈 Short-term Availability Trend (Bikes vs. Docks)")
    hist = get_snapshot_history()
    if isinstance(hist, list) or len(hist) < 2:
        st.info("Collecting snapshots. Come back in a minute for trends!")
    else:
        trend_obj = short_term_trend_chart(hist)
        st.plotly_chart(trend_obj["fig"], use_container_width=True)

with right:
    st.subheader("🏆 Top Stations by Available Bikes (Live)")
    # Interactive bar: click a bar to drill down
    fig_bar = top_stations_bar(df, n=12)
    selected = plotly_events(fig_bar, click_event=True, hover_event=False, select_event=False, key="top_stations_click")
    if selected:
        cd = selected[0].get("customdata") or []
        # customdata: [name, percent_full, bikes, docks]
        if cd:
            st.markdown("---")
            station_name = cd[0]
            bikes = int(cd[2])
            docks = int(cd[3])
            capacity = max(bikes + docks, 1)
            st.markdown(f"**{station_name}**")
            st.plotly_chart(station_utilization_gauge(station_name, bikes, capacity), use_container_width=True)
            cA, cB, cC = st.columns(3)
            cA.metric("Bikes", bikes)
            cB.metric("Docks", docks)
            cC.metric("Utilization", f"{(bikes/capacity)*100:.1f}%")
    else:
        # Non-interactive fallback render
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("#### 🗓 Last Updated")
st.caption(human_time(datetime.utcnow()) + " UTC • Record a new snapshot roughly every minute when you refresh")
st.success("Use the sidebar to dive into Stations, Trends, Models Lab, Fun Facts, Quiz, Story Builder, and the Live Map.")