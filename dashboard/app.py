from pathlib import Path

import streamlit as st


ASSET_DIR = Path(__file__).resolve().parent / "assets"

PERIODS = {
    "Morning: 8:00 am": "morning.png",
    "Daytime: 12:00 pm": "daytime.png",
    "Evening: 6:00 pm": "evening.png",
    "Night: 10:00 pm": "night.png",
}


st.set_page_config(
    page_title="Brisbane travel-time maps",
    page_icon="🗺️",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #f3f5f7; }
      header[data-testid="stHeader"],
      [data-testid="stToolbar"] { display: none; }
      .block-container {
        max-width: 1120px;
        padding-top: .65rem;
        padding-bottom: .65rem;
      }
      h1 {
        color: #162033;
        font-size: clamp(1.45rem, 2.6vw, 2rem) !important;
        letter-spacing: -0.025em;
        margin-bottom: .3rem !important;
      }
      .legend {
        align-items: center;
        color: #4b5565;
        display: flex;
        flex-wrap: wrap;
        font-size: .9rem;
        gap: .7rem 1.15rem;
        margin: 0 0 .45rem;
      }
      .legend-item {
        align-items: center;
        display: inline-flex;
        gap: .4rem;
      }
      .swatch {
        border-radius: 50%;
        display: inline-block;
        height: .72rem;
        width: .72rem;
      }
      [data-baseweb="tab-list"] { gap: .35rem; }
      [data-baseweb="tab"] {
        background: #ffffff;
        border: 1px solid #d3d9e0;
        padding: .55rem .85rem;
      }
      [data-baseweb="tab"][aria-selected="true"] {
        border-color: #162033;
        color: #162033;
      }
      [data-testid="stImage"] {
        display: flex;
        justify-content: center;
      }
      [data-testid="stImage"] img {
        border: 1px solid #c7ced7;
        height: auto !important;
        max-height: calc(100vh - 205px);
        max-height: calc(100dvh - 205px);
        max-width: 100% !important;
        object-fit: contain;
        width: auto !important;
      }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Brisbane travel-time maps")

st.markdown(
    """
    <div class="legend" aria-label="Map legend">
      <span class="legend-item"><span class="swatch" style="background:#0072B2"></span>Walking faster</span>
      <span class="legend-item"><span class="swatch" style="background:#F0E442"></span>About equal</span>
      <span class="legend-item"><span class="swatch" style="background:#D55E00"></span>Public transport faster</span>
      <span class="legend-item"><span class="swatch" style="background:#6A3D9A"></span>Comparison unavailable</span>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(list(PERIODS))
for tab, image_name in zip(tabs, PERIODS.values()):
    with tab:
        st.image(ASSET_DIR / image_name, use_container_width=True)
