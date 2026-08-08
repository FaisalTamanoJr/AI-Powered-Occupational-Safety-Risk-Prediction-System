import tempfile

import config
import streamlit as st
from pipeline import analyze_video, compute_video_risk, load_models

st.set_page_config(page_title="Workplace Safety Video Analyzer", layout="wide")
st.title("Workplace Safety Video Analyzer")

HAZARD_MODEL_PATH = "models/hazard.pt"
PPE_MODEL_PATH = "models/ppe.pt"

TIER_COLORS = {
    "Low": "#2e7d32",
    "Medium": "#f9a825",
    "High": "#e53935",
    "Critical": "#8e0000",
}


@st.cache_resource
def get_models():
    return load_models(HAZARD_MODEL_PATH, PPE_MODEL_PATH)


hazard_model, ppe_model = get_models()

uploaded_file = st.file_uploader(
    "Upload a workplace video", type=["mp4", "mov", "avi", "mkv"]
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(uploaded_file.read())
        video_path = tmp.name

    progress_bar = st.progress(0.0, text="Analyzing video...")

    def update_progress(pct):
        progress_bar.progress(pct, text=f"Analyzing video... {int(pct * 100)}%")

    tracked, timeline = analyze_video(
        video_path, hazard_model, ppe_model, progress_callback=update_progress
    )
    progress_bar.empty()

    result = compute_video_risk(tracked)

    video_col, summary_col = st.columns([1, 4])

    with video_col:
        st.video(video_path)

    with summary_col:
        st.subheader("Risk Summary")
        st.metric("Overall Risk Score", result["score"])
        tier = result["tier"]
        color = TIER_COLORS.get(tier, "gray")
        st.markdown(
            f"<h2 style='color:{color}'>{tier} Risk</h2>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("Confirmed Violations")
    if result["violations"]:
        rows = []
        for cls_name, rec in result["violations"].items():
            avg_conf = rec.total_confidence / max(rec.occurrences, 1)
            rows.append(
                {
                    "Violation": cls_name,
                    "Type": "Hazard" if rec.source == "hazard" else "PPE",
                    "First Confirmed (s)": round(rec.first_confirmed_time, 1),
                    "Last Seen (s)": round(rec.last_seen_time, 1),
                    "Confirmed Frames": rec.confirmed_frame_count,
                    "Avg Confidence": round(avg_conf, 2),
                    "Max Confidence": round(rec.max_confidence, 2),
                }
            )
        st.dataframe(rows, use_container_width=True)
    else:
        st.success("No sustained violations detected.")

    if timeline:
        st.subheader("Risk Score Over Time")
        scores = [s for _, s in timeline]
        st.line_chart({"Risk Score": scores})

    st.caption(
        f"Persistence threshold: {config.PERSISTENCE_FRAMES} consecutive analyzed "
        f"frames (every {config.FRAME_SKIP}th frame sampled, "
        f"conf ≥ {config.CONFIDENCE_THRESHOLD})."
    )
else:
    st.info("Upload a video to run hazard and PPE compliance analysis.")
