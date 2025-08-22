import pandas as pd
import numpy as np

def create_mock_station_data():
    """Create mock Citi Bike station data for demo purposes"""
    np.random.seed(42)  # For consistent demo data
    
    station_names = [
        "Central Park South & 6th Ave", "Grand Central Terminal", "Union Square East", 
        "Times Square", "Brooklyn Bridge", "High Line", "Chelsea Market",
        "Madison Square Park", "Washington Square Park", "Bryant Park",
        "Columbus Circle", "Flatiron Building", "Wall Street", "SoHo",
        "East Village", "Williamsburg", "DUMBO", "Park Slope", "Long Island City",
        "Astoria Park", "Prospect Park", "Red Hook", "Greenpoint", "Carroll Gardens"
    ]
    
    data = []
    for i, name in enumerate(station_names):
        bikes = np.random.randint(0, 25)
        docks = np.random.randint(5, 30)
        capacity = bikes + docks
        
        data.append({
            'station_id': f'mock_{i:03d}',
            'name': name,
            'lat': 40.7589 + np.random.uniform(-0.1, 0.1),
            'lon': -73.9851 + np.random.uniform(-0.15, 0.15),
            'num_bikes_available': bikes,
            'num_docks_available': docks,
            'capacity': capacity,
            'percent_full': bikes / capacity if capacity > 0 else 0,
            'last_reported': '2025-08-22T17:41:19+00:00',
            'last_updated_utc': pd.Timestamp.now(tz='UTC')
        })
    
    return pd.DataFrame(data)

def create_mock_history():
    """Create mock snapshot history data"""
    np.random.seed(42)
    timestamps = pd.date_range(
        start=pd.Timestamp.now() - pd.Timedelta(hours=3),
        end=pd.Timestamp.now(),
        freq='1min'
    ).tz_localize('UTC')
    
    base_bikes = 300
    base_docks = 400
    
    data = []
    for ts in timestamps:
        # Add some realistic variation
        bikes = base_bikes + np.random.randint(-50, 50)
        docks = base_docks + np.random.randint(-60, 60)
        
        data.append({
            'ts': ts,
            'total_bikes': max(bikes, 50),
            'total_docks': max(docks, 100),
            'avg_percent_full': np.random.uniform(0.3, 0.8)
        })
    
    return pd.DataFrame(data)