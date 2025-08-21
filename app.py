import os
import re
import streamlit as st
from dotenv import load_dotenv

from utils.vectorstore import VectorStore
from utils.db import HistoryDB
from services.document_parse import parse_document
from services.solar import answer_question, generate_quiz, plan_study_route

# 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("UPSTAGE_API_KEY")
SQLITE_PATH = os.getenv("SQLITE_PATH", "./study.db")
VECTOR_DIR = os.getenv("VECTOR_DB_DIR", "./data/index")

st.set_page_config(page_title="StudyStage Pro", layout="wide")


# Init
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = VectorStore()

vs = st.session_state.vectorstore
db = HistoryDB(SQLITE_PATH)


# UI
st.title("📚 StudyStage — 맞춤형 학습 코치")

tab_upload, tab_qa, tab_quiz, tab_plan = st.tabs(
    ["1) 문서 업로드", "2) Q&A", "3) Quiz ", "4) 학습 루트 추천"]
)

# 문서 업로드
with tab_upload:
    st.subheader("문서 업로드 & 인덱싱")
    files = st.file_uploader("PDF/이미지 업로드", type=["pdf", "png", "jpg"], accept_multiple_files=True)

    if st.button("업로드 & 인덱싱", disabled=not files):
        with st.status("문서 파싱 & 인덱싱 중..."):
            for f in files:
                try:
                    st.write(f"🔍 {f.name} 파싱 시도")
                    text = parse_document(f, api_key=API_KEY)
                    st.write(f"📄 추출된 텍스트 길이: {len(text)}")
                    st.text_area("📋 추출된 텍스트 일부", text[:1000], height=200)

                    if not text.strip():
                        st.warning(f"⚠️ {f.name} 에서 텍스트를 추출하지 못했습니다.")
                    else:
                        meta = {"filename": f.name}
                        st.write("🧠 벡터화 시도 중...")
                        vs.add_document(text, metadata=meta)
                        st.success(f"✅ {f.name} 업로드 완료")

                except Exception as e:
                    st.error(f"{f.name} 처리 중 오류: {e}")
        st.success("✅ 모든 업로드 완료! Q&A/퀴즈/플랜 탭에서 사용하세요.")

    if st.button("📦 현재 저장된 문서 확인"):
        st.write("총 저장 문서 수:", len(vs.vectors))
        for i, (_, text, meta) in enumerate(vs.vectors, 1):
            st.markdown(f"**[{i}] {meta.get('filename', 'unknown')}** — {text[:100]}...")

# ❓ Q&A
with tab_qa:
    st.subheader("멀티문서 Q&A")
    q = st.text_input("질문을 입력하세요", placeholder="예) 5주차 SVM 핵심 개념 요약해줘")
    if st.button("질문하기", disabled=not q):
        contexts = vs.search(q, top_k=5)
        if not contexts:
            st.warning("⚠️ 검색된 컨텍스트가 없습니다. 먼저 문서를 업로드하세요.")
        else:
            answer = answer_question(q, contexts=contexts, api_key=API_KEY)
            st.markdown("### 🧠 답변")
            st.write(answer)
            with st.expander("📂 참조 문서 보기"):
                for i, ctx in enumerate(contexts, 1):
                    st.markdown(f"**[{i}] {ctx['metadata'].get('filename','unknown')}**")
                    st.write(ctx["text"][:500])

# 📝 퀴즈 생성 탭
with tab_quiz:
    st.subheader("업로드 문서 기반 퀴즈 생성")

    topic_options = [
        "전체 요약",
        "주요 개념 정리",
        "기출 문제 패턴 퀴즈",
        "직접 입력"
    ]
    selected_topic = st.selectbox("퀴즈 주제 선택", topic_options)

    if selected_topic == "직접 입력":
        topic = st.text_input("퀴즈 주제 입력", placeholder="예: 3주차 회귀분석 요약")
    else:
        topic = selected_topic

    level = st.selectbox("난이도 선택", ["쉬움", "중간", "어려움"])

    if st.button("퀴즈 만들기", disabled=not topic):
        contexts = vs.search(topic, top_k=5)
        if not contexts:
            st.warning("⚠️ 문서를 먼저 업로드하세요.")
        else:
            quiz = generate_quiz(topic=topic, level=level, contexts=contexts, api_key=API_KEY)
            st.session_state["quiz_text"] = quiz

    if "quiz_text" in st.session_state:
        st.markdown("## 🎯 퀴즈")
        quiz = st.session_state["quiz_text"]

        raw_questions = re.split(r"Q\d+\.", quiz)
        raw_questions = [q.strip() for q in raw_questions if q.strip()]
        questions = [q for q in raw_questions if not q.startswith("###")]

        for i, q in enumerate(questions):
            answer_match = re.search(r"정답[^\d]*([①②③④])", q)
            explanation_match = re.search(r"해설[:：]?\s*(.*)", q)

            answer = answer_match.group(1) if answer_match else None
            explanation = explanation_match.group(1).strip() if explanation_match else None

            q = re.sub(r"정답[^\n]*", "", q)
            q = re.sub(r"해설[:：]?.*", "", q)

            choices = re.findall(r"[①②③④].*", q)
            question_text = q.splitlines()[0].strip()
            choices = [c.strip() for c in choices if not c.startswith("정답")]

            st.markdown(f"**Q{i+1}. {question_text}**")

            radio_key = f"quiz_{i}_selected"
            if radio_key not in st.session_state:
                st.session_state[radio_key] = None

            selected = st.radio("선택하세요:", choices, key=radio_key, index=None, label_visibility="collapsed")

            if selected:
                if answer:
                    if selected.startswith(answer):
                        st.success("✅ 정답입니다!")
                    else:
                        st.error(f"❌ 오답입니다. 정답은 {answer} 입니다.")

                if explanation:
                    st.markdown(f"📘 **해설:** {explanation}")


# 📌 학습 루트 추천 탭
with tab_plan:
    st.subheader("학습 루트 추천")

    goal_options = [
        "기초 개념 정리",
        "면접 대비 핵심 복습",
        "핵심 요약",
        "장기적 학습 루틴",
        "직접 입력"
    ]
    selected_goal = st.selectbox("학습 목표 선택", goal_options)

    if selected_goal == "직접 입력":
        goal = st.text_input("학습 목표 입력", placeholder="예: 2주 안에 통계 기반 회귀분석 마스터")
    else:
        goal = selected_goal

    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("학습 기간 (일)", 3, 30, 14)
    with col2:
        hours = st.slider("하루 학습 시간 (시간)", 1, 8, 2)

    if st.button("📌 학습 루트 추천받기", disabled=not goal):
        plan = plan_study_route(goal=goal, days=days, hours=hours, api_key=API_KEY)
        st.markdown("### 🧭 추천 학습 루트")
        st.write(plan)
