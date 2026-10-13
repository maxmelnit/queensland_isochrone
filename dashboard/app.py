from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
DATA_DIR = APP_DIR / "data"

PERIOD_DETAILS = {
    "Morning": {"time": "8:00 am", "image": "morning.png"},
    "Daytime": {"time": "12:00 pm", "image": "daytime.png"},
    "Evening": {"time": "6:00 pm", "image": "evening.png"},
    "Night": {"time": "10:00 pm", "image": "night.png"},
}

STATUS_LABELS = {
    "walking_faster": "Walking faster",
    "about_equal": "About equal",
    "transit_faster": "Public transport faster",
    "comparison_unavailable": "Comparison unavailable",
}

STATUS_COLOURS = {
    "Walking faster": "#0072B2",
    "About equal": "#F0E442",
    "Public transport faster": "#D55E00",
    "Comparison unavailable": "#6A3D9A",
}


st.set_page_config(
    page_title="Brisbane travel-time comparison",
    page_icon="🗺️",
    layout="wide",
)

st.markdown(
    """
    <style>
      .stApp { background: #f3f5f7; }
      .block-container { max-width: 1280px; padding-top: 2.2rem; padding-bottom: 3rem; }
      h1, h2, h3 { letter-spacing: -0.025em; }
      h1 { color: #162033; font-size: clamp(2rem, 4vw, 3.5rem) !important; }
      [data-testid="stMetric"] {
        background: #ffffff;
        border-top: 3px solid #162033;
        padding: 1rem 1.1rem;
      }
      [data-testid="stMetricLabel"] { color: #5e6878; }
      [data-testid="stMetricValue"] { color: #162033; }
      .project-kicker {
        color: #5e6878;
        font-size: .82rem;
        font-weight: 700;
        letter-spacing: .12em;
        margin-bottom: .5rem;
        text-transform: uppercase;
      }
      .project-summary { color: #4b5565; font-size: 1.06rem; max-width: 760px; }
      .map-frame img { border: 1px solid #cfd5dd; }
      .legend {
        align-items: center;
        color: #4b5565;
        display: flex;
        flex-wrap: wrap;
        font-size: .9rem;
        gap: .75rem 1.1rem;
        margin: .4rem 0 1.25rem;
      }
      .legend-item { align-items: center; display: inline-flex; gap: .38rem; }
      .swatch { border-radius: 50%; display: inline-block; height: .72rem; width: .72rem; }
      .method-note {
        border-left: 3px solid #162033;
        color: #4b5565;
        padding: .15rem 0 .15rem 1rem;
      }
      footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_summary() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "time_period_summary.csv")


summary = load_summary()
period = st.sidebar.selectbox(
    "Departure period",
    list(PERIOD_DETAILS),
    help="All scenarios use Thursday 17 September 2026.",
)

detail = PERIOD_DETAILS[period]
selected = summary.loc[summary["period"] == period].iloc[0]
included = int(selected["included_points"])
transit_share = 100 * selected["transit_faster"] / included
walking_share = 100 * selected["walking_faster"] / included

st.markdown('<div class="project-kicker">Spatial accessibility case study</div>', unsafe_allow_html=True)
st.title("Walking versus public transport in central Brisbane")
st.markdown(
    """
    <p class="project-summary">
      An interactive comparison of door-to-door travel times from Queen Street Mall
      across a 5 km × 5 km study area. The model combines a pedestrian street network
      with scheduled Translink services and supports journeys with up to two transfers.
    </p>
    """,
    unsafe_allow_html=True,
)

st.divider()
st.subheader(f"{period} departure · {detail['time']}")

metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("Mapped destinations", f"{included:,}")
metric_b.metric("Transit faster", f"{transit_share:.1f}%")
metric_c.metric("Walking faster", f"{walking_share:.1f}%")
metric_d.metric("Median advantage", f"{selected['median_difference_minutes']:.1f} min")

st.markdown(
    """
    <div class="legend">
      <span class="legend-item"><span class="swatch" style="background:#0072B2"></span>Walking faster</span>
      <span class="legend-item"><span class="swatch" style="background:#F0E442"></span>About equal</span>
      <span class="legend-item"><span class="swatch" style="background:#D55E00"></span>Public transport faster</span>
      <span class="legend-item"><span class="swatch" style="background:#6A3D9A"></span>Comparison unavailable</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="map-frame">', unsafe_allow_html=True)
st.image(ASSET_DIR / detail["image"], use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
st.caption(
    "Each dot represents one valid destination point. Water and unsuitable locations "
    "were removed before routing."
)

st.divider()
st.subheader("How the result changes by time of day")

outcome_columns = list(STATUS_LABELS)
chart_data = (
    summary[["period", *outcome_columns]]
    .melt(id_vars="period", var_name="status", value_name="destinations")
    .assign(
        outcome=lambda frame: frame["status"].map(STATUS_LABELS),
        period=lambda frame: pd.Categorical(
            frame["period"], categories=list(PERIOD_DETAILS), ordered=True
        ),
    )
)

chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("period:N", title=None, sort=list(PERIOD_DETAILS)),
        y=alt.Y("destinations:Q", title="Destination points"),
        color=alt.Color(
            "outcome:N",
            title=None,
            scale=alt.Scale(
                domain=list(STATUS_COLOURS),
                range=list(STATUS_COLOURS.values()),
            ),
            legend=alt.Legend(orient="bottom"),
        ),
        order=alt.Order("status:N", sort="ascending"),
        tooltip=[
            alt.Tooltip("period:N", title="Period"),
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("destinations:Q", title="Destinations", format=","),
        ],
    )
    .properties(height=340)
    .configure_view(stroke=None)
    .configure_axis(gridColor="#d9dee5", labelColor="#4b5565", titleColor="#4b5565")
)

st.altair_chart(chart, use_container_width=True)

with st.expander("Method and interpretation"):
    st.markdown(
        """
        <div class="method-note">
          Walking times were calculated over the OpenStreetMap pedestrian network using
          weighted shortest paths. Public-transport times include the walk to a stop,
          timetable waiting, travel on scheduled services, transfers, and the final walk
          to each destination. Results use a 90-minute routing horizon on Thursday
          17 September 2026. The median advantage is the median number of minutes by which
          the faster option beats the slower option at comparable destinations.
        </div>
        """,
        unsafe_allow_html=True,
    )

