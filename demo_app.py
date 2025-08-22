import streamlit as st
from datetime import datetime
from streamlit_plotly_events import plotly_events
from utils.mock_data import create_mock_station_data, create_mock_history
from utils.plots import kpi_cards, top_stations_bar, short_term_trend_chart, station_utilization_gauge
from utils.helpers import human_time
from utils.badges import init_badges, render_badges, track_page_visit
from utils.theme import inject_css

st.set_page_config(
    page_title="RidePulse NYC — Live Bike Intelligence (Demo)",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS animations/theme
inject_css()

# Create demo banner
st.sidebar.info("🎮 **DEMO MODE**: Using mock data to showcase interactive features!")

# Sidebar brand + badges
with st.sidebar:
    st.title("🚲 RidePulse NYC")
    st.caption("Live Bike Intelligence • Citi Bike GBFS")
    render_badges()
    st.markdown("---")
    refresh = st.button("🔄 Refresh Demo Data")
    st.caption("Use the sidebar Pages to explore everything.")

# Initialize achievements system
init_badges()
track_page_visit("Overview")

st.title("🚀 RidePulse NYC — Live Bike Intelligence")
st.info("🎮 **Demo Mode**: Showcasing interactive features with mock Citi Bike data. Click bars in the chart below to see drilldown!")

# Create mock data
df = create_mock_station_data()
hist = create_mock_history()

# KPIs
c1, c2, c3, c4 = st.columns(4)
kpi_cards(df, c1, c2, c3, c4)

# Highlights
st.markdown("### ⚡ Interactive Features Demo")
left, right = st.columns([2, 1])

with left:
    st.subheader("📈 Short-term Availability Trend (Mock Data)")
    trend_obj = short_term_trend_chart(hist)
    st.plotly_chart(trend_obj["fig"], use_container_width=True)

with right:
    st.subheader("🏆 Interactive Top Stations - Click Any Bar!")
    # Interactive bar: click a bar to drill down
    fig_bar = top_stations_bar(df, n=12)
    selected = plotly_events(fig_bar, click_event=True, hover_event=False, select_event=False, key="top_stations_click")
    
    if selected:
        cd = selected[0].get("customdata") or []
        # customdata: [name, percent_full, bikes, docks]
        if cd:
            st.markdown("---")
            st.success("🎯 **Clicked Station Details:**")
            station_name = cd[0]
            bikes = int(cd[2])
            docks = int(cd[3])
            capacity = max(bikes + docks, 1)
            
            st.markdown(f"**{station_name}**")
            
            # Show utilization gauge
            st.plotly_chart(station_utilization_gauge(station_name, bikes, capacity), use_container_width=True)
            
            # Metrics
            cA, cB, cC = st.columns(3)
            cA.metric("🚲 Bikes", bikes)
            cB.metric("🅿️ Docks", docks)
            cC.metric("📊 Fill %", f"{(bikes/capacity)*100:.1f}%")
            
            st.balloons()  # Celebrate the interaction!
    else:
        # Non-interactive fallback render
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("👆 Click on any bar above to see detailed station info!")

# Feature highlights
st.markdown("### 🌟 Enhanced Features Demonstrated")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎨 Dark Theme**
    - Automatic theme detection
    - Consistent styling across components
    - Enhanced visual hierarchy
    """)

with col2:
    st.markdown("""
    **🖱️ Interactive Charts**
    - Click-to-drill-down functionality
    - Rich hover information
    - Smooth animations and transitions
    """)

with col3:
    st.markdown("""
    **🏅 Smart Badge System**
    - Automatic page visit tracking
    - Persistent badge storage
    - Private award logging (no UI exposure)
    """)

st.markdown("### 🧩 All-in-One Dashboard")
st.info("Visit the **All-in-One** page in the sidebar to see all features consolidated into a single comprehensive view!")

st.markdown("#### 🗓 Demo Status")
st.caption(human_time(datetime.utcnow()) + " UTC • This demo showcases all interactive features using mock data")
st.success("✅ All enhanced features are working! Dark theme, interactive charts, badge persistence, and the new All-in-One dashboard are ready.")