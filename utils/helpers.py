from datetime import datetime

def human_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")