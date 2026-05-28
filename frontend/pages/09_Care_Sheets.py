from pathlib import Path

import streamlit as st

from frontend.ui.ui_framework.common import page_setup

MANUALS_DIR = Path(__file__).resolve().parents[2] / "backend" / "care_sheets" / "manuals"
IMAGES_DIR  = Path(__file__).resolve().parents[1] / "assets" / "care_sheet_images"
GRID_COLS   = 5


def filename_to_title(path: Path) -> str:
    return " ".join(w.capitalize() for w in path.stem.replace("-", " ").split())


page_setup(title="Care Sheets", icon="📋", page_heading="Care Sheets")

st.markdown(
    """
    <style>
    [data-testid="stImage"] img {
        border-radius: 10px;
        object-fit: cover;
        aspect-ratio: 1 / 1;
        width: 100%;
    }
    div[data-testid="stButton"] button {
        width: 100%;
        background: none;
        border: none;
        padding: 4px 0 12px 0;
        font-size: 12px;
        color: inherit;
        cursor: pointer;
        white-space: normal;
        text-align: center;
    }
    div[data-testid="stButton"] button:hover {
        text-decoration: underline;
        background: none;
        border: none;
        color: inherit;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

manuals   = sorted(MANUALS_DIR.glob("*.md"), key=lambda p: p.stem)
title_map = {m.stem: filename_to_title(m) for m in manuals}
path_map  = {m.stem: m for m in manuals}

selected_stem = st.query_params.get("manual")

if selected_stem and selected_stem in path_map:
    if st.button("← Back to Care Sheets"):
        st.query_params.clear()
        st.rerun()
    st.subheader(title_map[selected_stem])
    st.divider()
    st.markdown(path_map[selected_stem].read_text(encoding="utf-8"))

else:
    st.query_params.clear()
    items = list(title_map.items())
    for row_start in range(0, len(items), GRID_COLS):
        row = items[row_start : row_start + GRID_COLS]
        cols = st.columns(GRID_COLS)
        for col, (stem, title) in zip(cols, row):
            with col:
                img_path = IMAGES_DIR / f"{stem}.jpg"
                if img_path.exists():
                    st.image(str(img_path), use_container_width=True)
                else:
                    st.markdown(
                        '<div style="aspect-ratio:1;background:#1e3a1e;border-radius:10px;'
                        'display:flex;align-items:center;justify-content:center;font-size:40px">🦎</div>',
                        unsafe_allow_html=True,
                    )
                if st.button(title, key=f"btn_{stem}"):
                    st.query_params["manual"] = stem
                    st.rerun()
