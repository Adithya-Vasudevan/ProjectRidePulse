import streamlit as st
from utils.badges import award_badge, track_page_visit

st.set_page_config(page_title="Quiz • RidePulse NYC", page_icon="🧩", layout="wide")
track_page_visit("Quiz")

st.title("🧩 Citi Bike Quiz")

QUESTIONS = [
    {"q": "Citi Bike live data comes from which standard?", "options": ["GBFS", "GTFS", "OSM"], "a": "GBFS"},
    {"q": "If a station is 100% full, what does it mean?", "options": ["No docks free", "No bikes available", "Station is closed"], "a": "No docks free"},
    {"q": "Which factor most affects rush-hour ridership?", "options": ["Commute times", "Moon phases", "Random chance"], "a": "Commute times"},
    {"q": "The hex heatmap encodes…", "options": ["Available bikes per area", "Bike speeds", "User ages"], "a": "Available bikes per area"},
    {"q": "Arcs depict suggested flows from…", "options": ["Near-empty → near-full", "Near-full → near-empty", "Random"], "a": "Near-full → near-empty"},
]

if "quiz_i" not in st.session_state:
    st.session_state.quiz_i = 0
    st.session_state.score = 0

i = st.session_state.quiz_i
if i >= len(QUESTIONS):
    st.success(f"Done! Score: {st.session_state.score}/{len(QUESTIONS)}")
    if st.session_state.score == len(QUESTIONS):
        award_badge("quiz_whiz")
        st.balloons()
    if st.button("Play Again"):
        st.session_state.quiz_i = 0
        st.session_state.score = 0
    st.stop()

q = QUESTIONS[i]
st.subheader(q["q"])
for opt in q["options"]:
    if st.button(opt, use_container_width=True):
        if opt == q["a"]:
            st.session_state.score += 1
        st.session_state.quiz_i += 1
        st.rerun()

st.caption(f"Question {i+1} of {len(QUESTIONS)} • Score: {st.session_state.score}")