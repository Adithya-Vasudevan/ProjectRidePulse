import streamlit as st
import pandas as pd
import plotly.express as px
from utils.gbfs import get_snapshot_history
from utils.badges import award_badge, track_page_visit

st.set_page_config(page_title="Trends • RidePulse NYC", page_icon="📈", layout="wide")
track_page_visit("Trends")
award_badge("trend_hunter")

st.title("📈 Trends from Recent Snapshots")
hist = get_snapshot_history()

if isinstance(hist, list) or len(hist) < 5:
    st.info("Collecting snapshot history. Come back in a few minutes to see richer trends.")
else:
    df = hist.copy()
    df["ts_local"] = pd.to_datetime(df["ts"]).dt.tz_convert(None)

    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.line(df, x="ts_local", y=["total_bikes","total_docks"], title="Bikes and Docks Over Time", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.line(df, x="ts_local", y="avg_percent_full", title="Average Station Fill (%)", markers=True)
        fig2.update_traces(line_color="#f59e0b")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Derived Patterns")
    st.write("• Commute windows often show sharper changes. • Watch for synchronized rises in docks (return waves).")