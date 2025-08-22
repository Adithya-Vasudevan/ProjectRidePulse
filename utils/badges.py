import streamlit as st

BADGE_CATALOG = {
    "explorer": ("Explorer", "🧭"),
    "station_sage": ("Station Sage", "🏙️"),
    "trend_hunter": ("Trend Hunter", "📈"),
    "forecaster": ("Forecaster", "🔮"),
    "fact_finder": ("Fact Finder", "🔎"),
    "quiz_whiz": ("Quiz Whiz", "🧠"),
    "storyteller": ("Storyteller", "📖"),
    "cartographer": ("Cartographer", "🗺️"),
}

def init_badges():
    if "badges" not in st.session_state:
        st.session_state.badges = set()

def award_badge(key: str):
    init_badges()
    if key in BADGE_CATALOG:
        st.session_state.badges.add(key)

def render_badges():
    init_badges()
    if not st.session_state.badges:
        st.caption("No badges yet — explore pages to earn!")
        return
    st.markdown("#### 🏅 Badges")
    cols = st.columns(4)
    i = 0
    for key in sorted(st.session_state.badges):
        label, emoji = BADGE_CATALOG[key]
        with cols[i % 4]:
            st.button(f"{emoji} {label}", disabled=True)
        i += 1