# 📘 StudyStage Pro

> **멀티문서 기반 맞춤 학습 코치**  
> 학습 문서를 업로드하면, 자동으로 요약·Q&A·퀴즈·학습 루트를 추천해주는 올인원 AI 학습 보조 플랫폼

---

## 🧠 소개

**StudyStage Pro**는 Upstage API를 기반으로 다음 기능을 지원합니다:

- 여러 문서를 한번에 업로드하고 통합 관리
- 문서 기반 질의응답 (Q&A) 기능
- AI 기반 개념 퀴즈 생성 및 난이도 조절
- 목표/학습 시간에 맞춘 학습 루트 자동 추천

---

## 🔍 주요 기능

| 기능                 | 설명 |
|----------------------|------|
| 📄 **문서 업로드**      | PDF, 텍스트 등 다양한 문서를 통합하여 업로드 |
| 🧾 **정보 추출/요약**   | Upstage의 Document Parse & Information Extract API로 문서 구조화 |
| 💬 **Q&A 기능**         | 여러 문서에서 관련 내용을 검색 후 답변 (RAG 기반) |
| 🎯 **퀴즈 생성**        | 주제별 개념 퀴즈 생성 (난이도 선택 가능) |
| 🧭 **학습 루트 추천**   | 학습 목표와 기간에 맞춰 맞춤형 루트 제안 |

---

## 🛠️ 기술 스택

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend API**: [Upstage API (Parse / Extract / Solar)](https://docs.upstage.ai/)
- **Embedding & Vector Search**: Upstage Solar API
- **Python Version**: 3.10+
- **환경 구성**: `venv`, `.env` 파일 사용

---