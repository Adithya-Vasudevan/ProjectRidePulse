import streamlit as st
import pydeck as pdk
from utils.gbfs import merged_station_frame
from utils.badges import award_badge

st.set_page_config(page_title="Live Map • RidePulse NYC", page_icon="🗺️", layout="wide")
award_badge("cartographer")

st.title("🗺️ Live Map")

df = merged_station_frame().copy()
if len(df) == 0:
    st.info("No station data available.")
    st.stop()

df_map = df.rename(columns={"lat":"latitude","lng":"longitude"})

INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=40.7580, longitude=-73.9855, zoom=11, pitch=35
)

scatter = pdk.Layer(
    "ScatterplotLayer",
    data=df_map,
    get_position=["longitude", "latitude"],
    get_radius="(num_bikes_available+1)*3",
    get_fill_color="[percent_full*255, 120, 200, 160]",
    pickable=True,
    auto_highlight=True
)

hex_layer = pdk.Layer(
    "HexagonLayer",
    data=df_map,
    get_position=["longitude", "latitude"],
    radius=150,
    elevation_scale=4,
    elevation_range=[0, 1200],
    extruded=True,
    coverage=0.8,
    get_weight="num_bikes_available"
)

donors = df_map.sort_values("percent_full", ascending=False).head(6).reset_index(drop=True)
receivers = df_map.sort_values("percent_full", ascending=True).head(6).reset_index(drop=True)
pair_n = min(len(donors), len(receivers))
arcs_data = []
for i in range(pair_n):
    d = donors.iloc[i]; r = receivers.iloc[i]
    arcs_data.append({
        "from_name": d["name"], "to_name": r["name"],
        "from_lon": float(d["longitude"]), "from_lat": float(d["latitude"]),
        "to_lon": float(r["longitude"]), "to_lat": float(r["latitude"]),
        "width": int(max(2, (d["percent_full"]*10)))
    })

arc_layer = pdk.Layer(
    "ArcLayer",
    data=arcs_data,
    get_source_position=["from_lon","from_lat"],
    get_target_position=["to_lon","to_lat"],
    get_width="width",
    get_tilt=15,
    get_source_color=[255, 130, 0],
    get_target_color=[0, 160, 255],
    pickable=True
)

r = pdk.Deck(
    layers=[hex_layer, scatter, arc_layer],
    initial_view_state=INITIAL_VIEW_STATE,
    tooltip={"text": "{name}\n🚲 {num_bikes_available}  🅿️ {num_docks_available}"}
)

st.pydeck_chart(r, use_container_width=True, height=660)

st.markdown("""
<div class="rp-fact" style="margin-top:10px;">
<b>Legend:</b> Color = fill level, Radius/Elevation = available bikes. Arcs suggest rebalancing (near-full → near-empty).
</div>
""", unsafe_allow_html=True)