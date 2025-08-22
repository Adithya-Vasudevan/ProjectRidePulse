import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

def moving_average_forecast(series: pd.Series, window: int = 5, horizon: int = 10):
    series = series.dropna()
    if len(series) == 0:
        return [np.nan]*horizon
    avg = series.tail(window).mean() if len(series) >= window else series.mean()
    return [float(avg)]*horizon

def holt_winters_like(series: pd.Series, alpha: float = 0.5):
    series = series.dropna()
    if len(series) == 0:
        return series
    level = series.iloc[0]
    smoothed = []
    for x in series:
        level = alpha * x + (1 - alpha) * level
        smoothed.append(level)
    return pd.Series(smoothed, index=series.index)

def classify_station_traffic(df_stations: pd.DataFrame, k: int = 3):
    if len(df_stations) == 0:
        return []
    X = np.column_stack([
        df_stations["percent_full"].fillna(0).values,
        df_stations["num_bikes_available"].fillna(0).values
    ])
    k = min(max(2, k), len(df_stations))  # ensure valid
    km = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = km.fit_predict(X)
    # order clusters by bikes dimension
    order = np.argsort(km.cluster_centers_[:, 1])
    mapping = {order[0]:"Low"}
    if k == 2:
        mapping[order[1]] = "High"
    elif k >= 3:
        mapping[order[1]] = "Medium"
        mapping[order[2]] = "High"
        for extra in order[3:]:
            mapping[extra] = "Medium"
    return [mapping[l] for l in labels]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    t1, t2 = np.radians(lat1), np.radians(lat2)
    g1, g2 = np.radians(lon1), np.radians(lon2)
    dt = t2 - t1
    dg = g2 - g1
    a = np.sin(dt/2)**2 + np.cos(t1)*np.cos(t2)*np.sin(dg/2)**2
    c = 2*np.arcsin(np.sqrt(a))
    return float(R * c)

def estimate_trip_duration_minutes(s1, s2, mean_speed_kmh=12.0):
    dist_km = haversine_km(s1["lat"], s1["lng"], s2["lat"], s2["lng"])
    mins = (dist_km / mean_speed_kmh) * 60.0
    adj = 1.15 if dist_km < 2 else (1.25 if dist_km < 5 else 1.35)
    return float(np.round(mins * adj, 1))

def rider_type_predictor(hour: int, duration_min: float):
    if (7 <= hour <= 10) or (16 <= hour <= 19):
        if duration_min <= 25:
            return "Likely Member (commute hour, short trip)"
        return "Mixed (commute hour)"
    if duration_min >= 30 and (11 <= hour <= 18):
        return "Likely Casual (midday, longer leisure ride)"
    return "Mixed"