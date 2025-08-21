import os
import requests

CHAT_URL = "https://api.upstage.ai/v1/chat/completions"

def extract_keywords(text: str, api_key: str = None, top_k: int = 5) -> list[str]:
    """
    문서에서 핵심 키워드를 추출하는 함수 (Upstage Chat API 기반)
    """
    if api_key is None:
        api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY is not set")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "solar-1-mini-chat",
        "messages": [
            {"role": "system", "content": "너는 문서 분석기야. 텍스트에서 핵심 키워드를 뽑아줘."},
            {"role": "user", "content": f"다음 문서에서 핵심 키워드 {top_k}개를 추출해줘. 불필요한 설명 없이, 쉼표로 구분해서 출력해.\n\n문서:\n{text}"}
        ]
    }

    resp = requests.post(CHAT_URL, headers=headers, json=data, timeout=120)
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]

    # 쉼표 기준으로 분리 → 리스트 변환
    keywords = [kw.strip() for kw in content.replace("\n", " ").split(",") if kw.strip()]
    return keywords[:top_k]
