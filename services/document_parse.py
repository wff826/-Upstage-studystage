import io
import os
import requests
import streamlit as st
from bs4 import BeautifulSoup

API_URL = "https://api.upstage.ai/v1/document-digitization"

def parse_document(file, api_key: str = None) -> str:
    """PDF/이미지 파일을 Upstage API로 파싱"""
    if api_key is None:
        api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY is not set")

    # 파일 읽기
    if hasattr(file, "read"):
        content = file.read()
        file.seek(0)
        filename = getattr(file, "name", "upload.pdf")
    else:
        with open(file, "rb") as f:
            content = f.read()
        filename = file

    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": "document-parse"}
    files = {"document": (filename, io.BytesIO(content))}

    # API 호출
    try:
        st.write(f"📡 Upstage API 요청 시작: {API_URL}")
        resp = requests.post(API_URL, headers=headers, data=data, files=files, timeout=120)
        st.write(f"📬 응답 상태 코드: {resp.status_code}")
        resp.raise_for_status()
    except Exception as e:
        st.error(f"❌ API 요청 실패: {e}")
        return ""

    data = resp.json()
    st.write("📦 응답 데이터 일부:", {k: data[k] for k in data if k != "content"})  # content 제외 요약 출력

    content = data.get("content", {})
    raw_html = content.get("html", "")
    st.write("🔍 추출된 HTML 길이:", len(raw_html))

    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator="\n").strip()
        st.write("🧪 파싱된 최종 텍스트 길이:", len(text))
        return text
    else:
        st.warning("⚠️ HTML 내 텍스트를 추출할 수 없습니다.")
        return ""
