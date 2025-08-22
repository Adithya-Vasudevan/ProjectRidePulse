import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from pathlib import Path

GBFS_INFO = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
GBFS_STATUS = "https://gbfs.citibikenyc.com/gbfs/en/station_status.json"
DATA_DIR = Path("data")
PARQUET = DATA_DIR / "snapshots.parquet"
CSV = DATA_DIR / "snapshots.csv"
SNAPSHOT_TTL_MIN = 1  # record a snapshot at most every 1 minute

DATA_DIR.mkdir(exist_ok=True)

@st.cache_data(ttl=60)
def station_information():
    r = requests.get(GBFS_INFO, timeout=15)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data["data"]["stations"])
    if "lon" in df.columns and "lng" not in df.columns:
        df.rename(columns={"lon": "lng"}, inplace=True)
    return df

@st.cache_data(ttl=30)
def station_status():
    r = requests.get(GBFS_STATUS, timeout=15)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data["data"]["stations"])
    df["last_reported_dt"] = pd.to_datetime(df["last_reported"], unit="s", utc=True)
    last_updated = datetime.fromtimestamp(data.get("last_updated", datetime.now().timestamp()), tz=timezone.utc)
    return df, last_updated

def merged_station_frame(force: bool=False):
    if force:
        station_information.clear()
        station_status.clear()
    info = station_information()
    status, last_updated = station_status()
    df = info.merge(status, on="station_id", how="left", suffixes=("", "_status"))
    # derive metrics
    df["num_bikes_available"] = df["num_bikes_available"].fillna(0).astype(int)
    df["num_docks_available"] = df["num_docks_available"].fillna(0).astype(int)
    if "capacity" not in df.columns or df["capacity"].isna().all():
        cap = df["num_bikes_available"] + df["num_docks_available"]
    else:
        cap = df["capacity"].fillna(df["num_bikes_available"] + df["num_docks_available"])
    cap = cap.replace(0, 1)
    df["percent_full"] = (df["num_bikes_available"] / cap).clip(0, 1)
    df["last_updated_utc"] = last_updated
    return df

def _load_snapshots_df():
    if PARQUET.exists():
        try:
            return pd.read_parquet(PARQUET)
        except Exception:
            pass
    if CSV.exists():
        try:
            return pd.read_csv(CSV)
        except Exception:
            pass
    return pd.DataFrame()

def _save_snapshots_df(df_snap):
    try:
        df_snap.to_parquet(PARQUET, index=False)
    except Exception:
        df_snap.to_csv(CSV, index=False)

def record_snapshot_if_due(df: pd.DataFrame):
    """
    Append a compact snapshot of totals to local history at most once per minute.
    """
    hist = _load_snapshots_df()
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    row = {
        "ts": now.isoformat(),
        "total_bikes": int(df["num_bikes_available"].sum()),
        "total_docks": int(df["num_docks_available"].sum()),
        "active_stations": int((df["is_installed"]==1).sum() if "is_installed" in df.columns else len(df)),
        "avg_percent_full": float(df["percent_full"].mean()),
    }
    if len(hist) == 0:
        _save_snapshots_df(pd.DataFrame([row]))
        return

    last_ts = pd.to_datetime(hist["ts"].max(), utc=True)
    if (now - last_ts) >= timedelta(minutes=SNAPSHOT_TTL_MIN):
        new_hist = pd.concat([hist, pd.DataFrame([row])], ignore_index=True)
        _save_snapshots_df(new_hist)

def get_snapshot_history(n: int = 180):
    """
    Return the last n snapshots (about 3 hours at 1-min cadence).
    """
    hist = _load_snapshots_df()
    if len(hist) == 0:
        return []
    hist["ts"] = pd.to_datetime(hist["ts"], utc=True)
    return hist.sort_values("ts").tail(n)