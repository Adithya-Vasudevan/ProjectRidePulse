import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def kpi_cards(df, c1, c2, c3, c4):
    total_bikes = int(df["num_bikes_available"].sum())
    total_docks = int(df["num_docks_available"].sum())
    stations = len(df)
    avg_full = float(df["percent_full"].mean() * 100)

    c1.metric("🚲 Available Bikes", f"{total_bikes:,}")
    c2.metric("🅿️ Open Docks", f"{total_docks:,}")
    c3.metric("📍 Active Stations", f"{stations:,}")
    c4.metric("⚙️ Avg Station Fill", f"{avg_full:.1f}%")

def top_stations_bar(df, n=10):
    top = df.sort_values("num_bikes_available", ascending=False).head(n).copy()
    top["label"] = top["name"].str.slice(0, 26) + top["name"].apply(lambda s: "…" if len(s) > 26 else "")
    fig = px.bar(
        top,
        x="label",
        y="num_bikes_available",
        color="percent_full",
        color_continuous_scale="Blues",
        title=f"Top {n} Stations — Available Bikes",
        labels={"label":"Station", "num_bikes_available":"Bikes"}
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=360)
    fig.update_xaxes(tickangle=40)
    return fig

def short_term_trend_chart(hist_df: pd.DataFrame):
    plot_df = hist_df.copy()
    plot_df["ts_local"] = plot_df["ts"].dt.tz_convert(None)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df["ts_local"], y=plot_df["total_bikes"],
                             mode="lines+markers", name="Total Bikes", line=dict(color="#2563eb")))
    fig.add_trace(go.Scatter(x=plot_df["ts_local"], y=plot_df["total_docks"],
                             mode="lines+markers", name="Total Docks", line=dict(color="#10b981")))
    fig.update_layout(title="Last Snapshots", height=360, legend=dict(orientation="h"))
    return {"fig": fig, "data": plot_df}

def utilization_hist(df):
    series = (df["percent_full"]*100).round(1)
    fig = px.histogram(series, nbins=30, title="Station Utilization (%)",
                       color_discrete_sequence=["#6366f1"], labels={"value":"% Full"})
    fig.update_layout(height=320, bargap=0.02)
    return fig