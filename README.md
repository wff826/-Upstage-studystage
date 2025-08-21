# StudyStage
멀티문서 기반 맞춤 학습 코치 (Upstage API: Document Parse / Information Extract / Solar)

## Features (MVP)
- PDF 업로드 → 문서 파싱
- 멀티문서 RAG 기반 Q&A
- 키워드/개념 추출
- 적응형 Quiz 생성
- 개인화 학습 루트 추천(목표/기간 기반)

## Quickstart
```bash
git clone <your-repo-url>
cd study-stage-pro
python -m venv .venv && source .venv/bin/activate 
cp .env.example .env 
streamlit run app.py
