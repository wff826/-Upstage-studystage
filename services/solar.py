import os
import requests

CHAT_URL = "https://api.upstage.ai/v1/chat/completions"

def _call_solar(messages: list, api_key: str = None, model: str = "solar-pro") -> str:
    if api_key is None:
        api_key = os.getenv("UPSTAGE_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": messages}

    resp = requests.post(CHAT_URL, headers=headers, json=data, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def _merge_contexts(contexts, max_chars=3000):
    buf, total = [], 0
    for c in contexts:
        t = c["text"]
        if total + len(t) > max_chars:
            t = t[: max_chars - total]
        buf.append(t)
        total += len(t)
        if total >= max_chars:
            break
    return "\n\n".join(buf)

def answer_question(question: str, contexts: list, api_key: str = None) -> str:
    """컨텍스트 기반 질문응답"""
    context_text = _merge_contexts(contexts, max_chars=3000)
    return _call_solar([
        {"role": "system", "content": "너는 주어진 문서를 기반으로 질문에 답하는 조력자야."},
        {"role": "user", "content": f"문서:\n{context_text}\n\n질문:\n{question}"}
    ], api_key)

def generate_quiz(topic: str, level: str = "중간", contexts: list = None, api_key: str = None) -> str:
    """업로드 문서 기반 퀴즈 생성"""
    context_text = _merge_contexts(contexts or [], max_chars=3000)

    prompt = f"""
너는 교사야. 아래 문맥을 바탕으로 학습용 객관식 퀴즈를 3~5문제 만들어줘.

[제약 조건]
- 문항 제목은 "Q1."부터 시작하되, 빈 문항은 포함하지 말 것
- 각 문제는 "Q1.", "Q2." 형식으로 시작
- 각 문제는 반드시 선택지 4개를 제공하고, 아래 형식을 따라야 해
- 선택지는 반드시 아래처럼 표기해야 함:
    ① 선택지 A
    ② 선택지 B
    ③ 선택지 C
    ④ 선택지 D
- 정답은 '정답: ①' 형태로 명시
- 해설은 '해설:'로 시작

[예시 형식]
Q1. 다음 중 파이썬의 특징이 아닌 것은?
① 들여쓰기를 문법으로 사용한다.
② 인터프리터 언어다.
③ 포인터 연산을 지원한다.
④ 동적 타이핑을 지원한다.
정답: ③
해설: 파이썬은 포인터 연산을 지원하지 않으며, 이는 C/C++의 특징이다.

[주제]
{topic}

[문맥]
{context_text}
"""

    return _call_solar([
        {"role": "system", "content": "너는 교사야. 문서를 바탕으로 학습용 퀴즈를 만든다."},
        {"role": "user", "content": prompt.strip()}
    ], api_key)



def plan_study_route(goal: str, days: int, hours: int, contexts: list = None, api_key: str = None):
    """문서 없이 학습 목표 기반 학습 루트 추천"""
    context_text = _merge_contexts(contexts or [], max_chars=3000) if contexts else ""

    prompt = f"""
    너는 전문 학습 플래너야. 사용자의 목표와 제약 조건을 고려해서 맞춤형 학습 계획을 세워.

    목표: {goal}
    기간: {days}일
    하루 학습 시간: {hours}시간

    {f"참고 자료:\n{context_text}" if context_text else "문서 없이 가능한 학습 루트를 추천해줘."}

    위 조건에 맞춰 하루 단위로 세부 학습 계획을 제시해줘.
    """

    return _call_solar([
        {"role": "system", "content": "너는 전문 학습 플래너야."},
        {"role": "user", "content": prompt}
    ], api_key)

