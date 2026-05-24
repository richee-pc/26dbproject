"""
자료구조 구현 프로젝트 · 수행평가 헬프데스크 (Streamlit 배포용)

전체 HTML(아코디언·시뮬레이션 JS)은 iframe으로 격리해 띄웁니다.
st.html()로 문서 전체를 넣으면 DOMContentLoaded가 이미 지나 JS가 안 돌고,
Streamlit CSS와 충돌해 디자인이 깨질 수 있습니다.
"""
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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

IFRAME_RESIZE_SNIPPET = """
<script>
(function () {
  function postHeight() {
    var h = Math.max(
      document.body ? document.body.scrollHeight : 0,
      document.documentElement ? document.documentElement.scrollHeight : 0,
      document.body ? document.body.offsetHeight : 0,
      document.documentElement ? document.documentElement.offsetHeight : 0
    );
  window.parent.postMessage({ type: "streamlit:setFrameHeight", height: h + 24 }, "*");
  }
  function schedule() { requestAnimationFrame(postHeight); }
  window.addEventListener("load", schedule);
  window.addEventListener("resize", schedule);
  if (typeof MutationObserver !== "undefined") {
    new MutationObserver(schedule).observe(document.documentElement, {
      childList: true, subtree: true, attributes: true, characterData: true
    });
  }
  setInterval(schedule, 800);
})();
</script>
"""


@st.cache_data(show_spinner=False)
def load_html() -> str:
    for path in HTML_CANDIDATES:
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if IFRAME_RESIZE_SNIPPET.strip() not in text:
                if "</body>" in text:
                    text = text.replace("</body>", IFRAME_RESIZE_SNIPPET + "\n</body>", 1)
                else:
                    text += IFRAME_RESIZE_SNIPPET
            return text
    raise FileNotFoundError(
        "dbproject.html을 찾을 수 없습니다. "
        "저장소에 assets/dbproject.html 이 있어야 합니다."
    )


def render_html(html: str) -> None:
    components.html(html, height=720, scrolling=True)


def main() -> None:
    st.markdown(
        """
        <style>
          #MainMenu, footer, header { visibility: hidden; height: 0; }
          .block-container { padding: 0 !important; max-width: 100% !important; }
          iframe { border: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    try:
        html = load_html()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    render_html(html)


if __name__ == "__main__":
    main()
