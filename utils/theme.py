import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
        /* Animated gradient background */
        body {
          background: linear-gradient(120deg, #eef2ff, #f0f9ff, #fdf2f8);
          background-size: 400% 400%;
          animation: gradientShift 28s ease infinite;
        }
        @keyframes gradientShift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }

        /* Container card feel */
        .main .block-container {
          backdrop-filter: saturate(120%) blur(3px);
        }

        /* KPI metric styling */
        div[data-testid="stMetric"] {
          background: #ffffffaa;
          border-radius: 14px;
          padding: 14px 16px;
          box-shadow: 0 6px 18px rgba(37, 99, 235, 0.08);
          border: 1px solid #e5e7eb;
        }
        div[data-testid="stMetric"]:hover {
          transform: translateY(-2px);
          transition: transform 200ms ease;
          box-shadow: 0 10px 22px rgba(37, 99, 235, 0.12);
        }

        /* Headings accent underline */
        h2, h3 {
          position: relative;
        }
        h2::after, h3::after {
          content: "";
          position: absolute;
          left: 0;
          bottom: -6px;
          width: 64px;
          height: 4px;
          background: linear-gradient(90deg, #2563eb, #22c55e, #f59e0b);
          border-radius: 4px;
          opacity: 0.85;
        }

        /* Subtle hover lift for charts */
        .stPlotlyChart, .stPydeckGlJsonChart {
          transition: transform 200ms ease, box-shadow 200ms ease;
        }
        .stPlotlyChart:hover, .stPydeckGlJsonChart:hover {
          transform: translateY(-3px);
          box-shadow: 0 12px 28px rgba(0,0,0,0.08);
        }

        /* Fact cards */
        .rp-fact {
          background: linear-gradient(180deg, #ffffff, #f8fafc);
          border: 1px solid #e5e7eb;
          border-radius: 14px;
          padding: 12px 14px;
          box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
        }

        /* Sidebar badges */
        .rp-badge {
          background: #f1f5f9;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 8px 10px;
        }
        </style>
        """
        ,
        unsafe_allow_html=True,
    )