import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from utils.gbfs import merged_station_frame, get_snapshot_history
from utils.models import moving_average_forecast, estimate_trip_duration_minutes, rider_type_predictor, classify_station_traffic
from utils.badges import award_badge

st.set_page_config(page_title="Models Lab • RidePulse NYC", page_icon="🧠", layout="wide")
award_badge("forecaster")

st.title("🧠 Models Lab — Interactive")
df = merged_station_frame()
hist = get_snapshot_history()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Short-term Ride Prediction",
    "Busiest Station Classifier",
    "Trip Duration Estimator",
    "Rider Type Predictor",
    "Weekend vs Weekday Explorer"
])

with tab1:
    st.subheader("Short-term Ride Prediction (Total Bikes)")
    if not (isinstance(hist, list) or len(hist) < 5):
        s = pd.Series([int(x) for x in hist["total_bikes"]], index=pd.to_datetime(hist["ts"]))
        fc = moving_average_forecast(s, window=5, horizon=10)
        idx = pd.date_range(s.index[-1], periods=len(fc)+1, freq="T")[1:]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=s.index, y=s.values, name="Observed", mode="lines", line=dict(color="#2563eb")))
        fig.add_trace(go.Scatter(x=idx, y=fc, name="Forecast", mode="lines", line=dict(color="#16a34a", dash="dash")))
        fig.update_layout(height=360, title="Next 10 minutes forecast")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need more snapshots to forecast. Try again later.")

with tab2:
    st.subheader("Traffic Levels (Live)")
    labels = classify_station_traffic(df)
    if labels:
        df2 = df.copy()
        df2["traffic"] = labels
        st.bar_chart(df2["traffic"].value_counts())
        st.dataframe(
            df2.sort_values("num_bikes_available", ascending=False)[["name","num_bikes_available","percent_full","traffic"]]
            .rename(columns={"name":"Station","num_bikes_available":"Bikes","percent_full":"% Full"})
            .assign(**{"% Full": (df2.sort_values("num_bikes_available", ascending=False)["percent_full"]*100).round(1)}).head(25),
            use_container_width=True,
            height=420
        )
    else:
        st.info("Not enough stations to classify.")

with tab3:
    st.subheader("Trip Duration Estimator (Start → End)")
    c1, c2, c3 = st.columns([2,2,1])
    start = c1.selectbox("Start Station", df["name"].sort_values().tolist())
    end = c2.selectbox("End Station", df["name"].sort_values().tolist(), index=1 if len(df)>1 else 0)
    speed = c3.slider("Avg Speed (km/h)", 8, 20, 12)
    s1 = df[df["name"]==start].iloc[0].to_dict()
    s2 = df[df["name"]==end].iloc[0].to_dict()
    est = estimate_trip_duration_minutes(s1, s2, mean_speed_kmh=speed)
    st.success(f"Estimated duration: {est} minutes")

with tab4:
    st.subheader("Rider Type Predictor")
    hour = st.slider("Start hour (0-23)", 0, 23, value=datetime.now().hour)
    duration = st.slider("Estimated trip duration (min)", 5, 120, 20)
    pred = rider_type_predictor(hour, duration)
    st.info(f"Prediction: {pred}")

with tab5:
    st.subheader("Weekend vs Weekday Pattern Explorer")
    if not (isinstance(hist, list) or len(hist) < 30):
        st.warning("Come back later after more snapshots are gathered.")
    else:
        temp = hist.copy()
        temp["dow"] = pd.to_datetime(temp["ts"]).dt.tz_convert(None).dt.day_name()
        chart = temp.groupby("dow")["total_bikes"].mean().reset_index()
        st.bar_chart(chart.set_index("dow"))