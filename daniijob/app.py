"""
자료구조 구현 프로젝트 · 수행평가 헬프데스크 (Streamlit 배포용)
"""
from pathlib import Path

import streamlit as st

# ── 페이지 설정 (맨 위에서 한 번만) ─────────────────────────────
st.set_page_config(
    page_title="자료구조 프로젝트 헬프데스크",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).resolve().parent
HTML_CANDIDATES = [
    ROOT / "assets" / "dbproject.html",
    ROOT / "dbproject.html",
]


@st.cache_data(show_spinner=False)
def load_html() -> str:
    for path in HTML_CANDIDATES:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "dbproject.html을 찾을 수 없습니다. "
        "저장소 루트에 assets/dbproject.html 이 있어야 합니다."
    )


def render_html(html: str) -> None:
    """아코디언·시뮬레이션 등 JS가 동작하려면 JavaScript 허용이 필요합니다."""
    if hasattr(st, "html"):
        st.html(html, unsafe_allow_javascript=True)
        return
    # 구버전 Streamlit 대비
    st.components.v1.html(html, height=1200, scrolling=True)


def main() -> None:
    try:
        html = load_html()
    except FileNotFoundError as e:
        st.error(str(e))
        st.markdown(
            """
            **GitHub 저장소에 아래 구조가 있는지 확인해 주세요.**

            ```
            app.py
            requirements.txt
            assets/dbproject.html
            ```

            `Main file`은 반드시 **`app.py`** 로 설정하세요.
            """
        )
        st.stop()

    # Streamlit 상단 여백 최소화
    st.markdown(
        """
        <style>
          header[data-testid="stHeader"] { background: transparent; }
          .block-container { padding-top: 1rem; max-width: 100%; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    render_html(html)


if __name__ == "__main__":
    main()
