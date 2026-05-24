"""
학습 헬프데스크 Streamlit 배포

- 자료구조 수행평가: assets/dbproject.html
- 컴퓨터 구조 4단원: assets/cs_4.html

HTML은 iframe(components.html)으로 띄워 JS·CSS가 정상 동작합니다.
제출 URL은 HTML 내장값을 쓰며, Streamlit Secrets의 google_submit_url 이 있으면 덮어씁니다.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
SUBMIT_URL_PLACEHOLDER = "PASTE_WEB_APP_URL_HERE"

# HTML에 넣은 URL과 동일하게 유지 (Secrets 없을 때 사용)
DEFAULT_GOOGLE_SUBMIT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzCS5Hdod0HNkDC4UWLN9glCu2FlvndpfQm-c94ozfWGgaiIYy2wrfSW1UGJCJJfMRufQ/exec"
)

PAGES: dict[str, dict] = {
    "dbproject": {
        "title": "자료구조 프로젝트",
        "subtitle": "수행평가 헬프데스크",
        "icon": "📦",
        "paths": [
            ROOT / "assets" / "dbproject.html",
            ROOT / "dbproject.html",
        ],
    },
    "cs4": {
        "title": "컴퓨터 구조 4단원",
        "subtitle": "메모리 탐험대",
        "icon": "🧠",
        "paths": [
            ROOT / "assets" / "cs_4.html",
        ],
    },
}

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

GOOGLE_SUBMIT_URL_RE = re.compile(
    r"var GOOGLE_SUBMIT_URL = '(https://script\.google\.com/macros/s/[^']+)'"
)


def google_submit_url() -> str:
    try:
        url = st.secrets.get("google_submit_url", "").strip()
        if url:
            return url
    except (AttributeError, KeyError, TypeError):
        pass
    env = os.environ.get("GOOGLE_SUBMIT_URL", "").strip()
    if env:
        return env
    return DEFAULT_GOOGLE_SUBMIT_URL


def inject_submit_url(html: str, url: str) -> str:
    if not url:
        return html
    if SUBMIT_URL_PLACEHOLDER in html:
        html = html.replace(f"'{SUBMIT_URL_PLACEHOLDER}'", f"'{url}'", 1)
    html, n = GOOGLE_SUBMIT_URL_RE.subn(
        f"var GOOGLE_SUBMIT_URL = '{url}'",
        html,
        count=1,
    )
    return html


def read_page_html(paths: list[Path]) -> str:
    for path in paths:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    names = ", ".join(str(p.relative_to(ROOT)) for p in paths)
    raise FileNotFoundError(f"HTML 파일을 찾을 수 없습니다: {names}")


@st.cache_data(show_spinner=False)
def load_html(page_key: str, submit_url: str) -> str:
    if page_key not in PAGES:
        raise ValueError(f"알 수 없는 페이지: {page_key}")

    text = read_page_html(PAGES[page_key]["paths"])
    text = inject_submit_url(text, submit_url)

    if IFRAME_RESIZE_SNIPPET.strip() not in text:
        if "</body>" in text:
            text = text.replace("</body>", IFRAME_RESIZE_SNIPPET + "\n</body>", 1)
        else:
            text += IFRAME_RESIZE_SNIPPET
    return text


def render_html(html: str) -> None:
    components.html(html, height=1600, scrolling=True)


def apply_chrome_hiding() -> None:
    st.markdown(
        """
        <style>
          #MainMenu, footer, header { visibility: hidden; height: 0; }
          .block-container { padding-top: 0.5rem !important; max-width: 100% !important; }
          iframe { border: none !important; }
          div[data-testid="stSegmentedControl"] { margin-bottom: 0.25rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def resolve_page_key() -> str:
    qp = st.query_params.get("page")
    if qp in PAGES:
        return str(qp)
    return "dbproject"


def page_label(key: str) -> str:
    p = PAGES[key]
    return f"{p['icon']} {p['title']}"


def main() -> None:
    st.set_page_config(
        page_title="학습 헬프데스크",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="auto",
    )

    apply_chrome_hiding()
    submit_url = google_submit_url()

    default_key = resolve_page_key()
    keys = list(PAGES.keys())
    default_index = keys.index(default_key) if default_key in keys else 0

    with st.sidebar:
        st.markdown("### 📚 수업 선택")
        page_key = st.radio(
            "페이지",
            options=keys,
            index=default_index,
            format_func=page_label,
            label_visibility="collapsed",
        )
        st.caption(PAGES[page_key]["subtitle"])
        st.divider()
        st.caption("제출 데이터 → 시트 **「제출_통합」**")
        st.caption("상세 JSON → Drive **학생_제출_통합**")
        if submit_url != DEFAULT_GOOGLE_SUBMIT_URL:
            st.caption("제출 URL: Secrets 적용됨")

    if st.query_params.get("page") != page_key:
        st.query_params["page"] = page_key

    try:
        html = load_html(page_key, submit_url)
    except (FileNotFoundError, ValueError) as e:
        st.error(str(e))
        st.stop()

    render_html(html)


if __name__ == "__main__":
    main()
