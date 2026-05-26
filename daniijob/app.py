"""
학습 헬프데스크 Streamlit 배포

- 자료구조 수행평가: assets/dbproject.html
- 컴퓨터 구조 4단원: assets/cs_4.html

HTML은 iframe(components.html)으로 띄워 JS·CSS가 정상 동작합니다.
"""
from __future__ import annotations

import base64
import mimetypes
import os
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

DEFAULT_GOOGLE_SUBMIT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzCS5Hdod0HNkDC4UWLN9glCu2FlvndpfQm-c94ozfWGgaiIYy2wrfSW1UGJCJJfMRufQ/exec"
)

PAGES = {
    "dbproject": {
        "title": "자료구조 프로젝트",
        "subtitle": "수행평가 헬프데스크",
        "icon": "📦",
        "file": "dbproject.html",
    },
    "cs4": {
        "title": "컴퓨터 구조 4단원",
        "subtitle": "메모리 탐험대",
        "icon": "🧠",
        "file": "cs_4.html",
    },
}

RESIZE_JS = """
<script>
(function(){
  function h(){
    var d=Math.max(
      document.body?document.body.scrollHeight:0,
      document.documentElement?document.documentElement.scrollHeight:0,
      document.body?document.body.offsetHeight:0,
      document.documentElement?document.documentElement.offsetHeight:0);
    window.parent.postMessage({type:"streamlit:setFrameHeight",height:d+32},"*");
  }
  function s(){requestAnimationFrame(h)}
  window.addEventListener("load",s);
  window.addEventListener("resize",s);
  if(typeof MutationObserver!=="undefined")
    new MutationObserver(s).observe(document.documentElement,
      {childList:true,subtree:true,attributes:true,characterData:true});
  setInterval(s,800);
})();
</script>
"""

_IMG_RE = re.compile(r'(<img\s[^>]*?)src="(images/[^"]+)"', re.I)
_SUBMIT_RE = re.compile(
    r"var GOOGLE_SUBMIT_URL\s*=\s*'(https://script\.google\.com/macros/s/[^']+)'"
)


def _get_submit_url() -> str:
    try:
        url = st.secrets.get("google_submit_url", "").strip()
        if url:
            return url
    except Exception:
        pass
    return os.environ.get("GOOGLE_SUBMIT_URL", "").strip() or DEFAULT_GOOGLE_SUBMIT_URL


def _embed_images(html: str, html_dir: Path) -> str:
    """상대 경로 이미지를 base64 data URI로 치환."""
    def _repl(m: re.Match) -> str:
        prefix, rel = m.group(1), m.group(2)
        img_path = html_dir / rel
        if not img_path.is_file():
            return m.group(0)
        mime = mimetypes.guess_type(img_path.name)[0] or "image/png"
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        return f'{prefix}src="data:{mime};base64,{b64}"'
    return _IMG_RE.sub(_repl, html)


def _inject_submit_url(html: str, url: str) -> str:
    if "PASTE_WEB_APP_URL_HERE" in html:
        html = html.replace("'PASTE_WEB_APP_URL_HERE'", f"'{url}'", 1)
    html = _SUBMIT_RE.sub(f"var GOOGLE_SUBMIT_URL = '{url}'", html, count=1)
    return html


def _prepare_html(page_key: str) -> str:
    info = PAGES[page_key]
    html_path = ASSETS / info["file"]
    if not html_path.is_file():
        raise FileNotFoundError(f"{info['file']}을 찾을 수 없습니다.")

    html = html_path.read_text(encoding="utf-8")
    html = _inject_submit_url(html, _get_submit_url())
    html = _embed_images(html, ASSETS)

    if "streamlit:setFrameHeight" not in html:
        if "</body>" in html:
            html = html.replace("</body>", RESIZE_JS + "</body>", 1)
        else:
            html += RESIZE_JS
    return html


def main() -> None:
    st.set_page_config(
        page_title="학습 헬프데스크",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="auto",
    )

    st.markdown(
        "<style>"
        "#MainMenu,footer,header{visibility:hidden;height:0}"
        ".block-container{padding-top:.5rem!important;max-width:100%!important}"
        "iframe{border:none!important}"
        "</style>",
        unsafe_allow_html=True,
    )

    keys = list(PAGES.keys())

    page_key = st.sidebar.radio(
        "수업 선택",
        options=keys,
        format_func=lambda k: f"{PAGES[k]['icon']} {PAGES[k]['title']}",
    )

    try:
        html = _prepare_html(page_key)
    except FileNotFoundError as e:
        st.error(str(e))
        return

    components.html(html, height=1600, scrolling=True)


if __name__ == "__main__":
    main()
