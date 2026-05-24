import streamlit as st
from pathlib import Path

st.set_page_config(page_title="자료구조 프로젝트 헬프데스크", layout="wide")

html = Path("assets/dbproject.html").read_text(encoding="utf-8")
st.components.v1.html(html, height=900, scrolling=True)
