import streamlit as st
import plotly.express as px
from utils.gbfs import merged_station_frame
from utils.plots import top_stations_bar, utilization_hist
from utils.badges import award_badge

st.set_page_config(page_title="Fun Facts • RidePulse NYC", page_icon="🎉", layout="wide")
award_badge("fact_finder")

st.title("🎉 Fun Facts — Live and Auto-Generated")
df = merged_station_frame()

# Top facts
cols = st.columns(3)
facts = [
    ("🏙️ Most Bikes Now", df.loc[df["num_bikes_available"].idxmax(), "name"] if len(df)>0 else "-"),
    ("🥇 Highest Fill %", df.loc[df["percent_full"].idxmax(), "name"] if len(df)>0 else "-"),
    ("🆓 Most Docks Free", df.loc[df["num_docks_available"].idxmax(), "name"] if len(df)>0 else "-"),
]
for i, (label, val) in enumerate(facts):
    with cols[i]:
        st.metric(label, val)

# Fact cards
st.markdown("### ✨ Live Fact Cards")
if len(df) > 0:
    facts_list = []
    facts_list.append(f"Total stations online: {len(df)}")
    facts_list.append(f"Citywide average fill: {(df['percent_full'].mean()*100):.1f}%")
    facts_list.append(f"Stations with zero bikes: {(df['num_bikes_available']==0).sum()}")
    facts_list.append(f"Stations with zero docks: {(df['num_docks_available']==0).sum()}")
    facts_list.append(f"Top 3 by bikes: {', '.join(df.sort_values('num_bikes_available',ascending=False).head(3)['name'].tolist())}")
    facts_list.append(f"Top 3 by docks: {', '.join(df.sort_values('num_docks_available',ascending=False).head(3)['name'].tolist())}")
    facts_list.append(f"Median available bikes: {int(df['num_bikes_available'].median())}")
    facts_list.append(f"Median open docks: {int(df['num_docks_available'].median())}")
    facts_list.append(f"Max capacity observed: {int((df['num_bikes_available']+df['num_docks_available']).max())}")
    facts_list.append(f"Avg bikes per station: {df['num_bikes_available'].mean():.1f}")

    rows = (len(facts_list) + 2)//3
    k = 0
    for _ in range(rows):
        c1, c2, c3 = st.columns(3)
        for c in [c1, c2, c3]:
            if k < len(facts_list):
                c.markdown(f"<div class='rp-fact'>• {facts_list[k]}</div>", unsafe_allow_html=True)
            k += 1
else:
    st.info("No stations available.")

# Visuals
st.markdown("### 🎯 Visual Tidbits")
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(top_stations_bar(df, n=15), use_container_width=True)
with col2:
    st.plotly_chart(utilization_hist(df), use_container_width=True)

st.balloons()