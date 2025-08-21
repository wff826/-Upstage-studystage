import os
import requests
import numpy as np
import textwrap
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st


class VectorStore:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.vectors = []  # (embedding, text, metadata)

    def get_embedding(self, text: str):
        url = "https://api.upstage.ai/v1/embeddings"
        model = "embedding-query"

        chunks = textwrap.wrap(text, 1000)
        embeddings = []

        st.write(f"📐 총 {len(chunks)}개 청크로 분할 (각 최대 1000자)")

        for i, chunk in enumerate(chunks, 1):
            payload = {"input": chunk, "model": model}
            try:
                res = requests.post(url, headers=self.headers, json=payload)
                res.raise_for_status()
                emb = res.json()["data"][0]["embedding"]
                embeddings.append(emb)
                st.write(f"✅ Chunk {i} 임베딩 완료 (벡터 길이: {len(emb)})")
            except Exception as e:
                st.error(f"❌ Chunk {i} 임베딩 실패: {e}")
                continue

        if not embeddings:
            raise RuntimeError("❌ 모든 chunk 임베딩 실패. 벡터 생성 불가")

        avg_embedding = np.mean(np.array(embeddings), axis=0)
        return avg_embedding.tolist()

    def add_document(self, text, metadata=None):
        try:
            if not text.strip():
                st.warning("⚠️ 빈 텍스트입니다. 벡터화 건너뜀")
                return
            st.write(f"📝 문서 텍스트 길이: {len(text)}")
            emb = self.get_embedding(text)
            self.vectors.append((np.array(emb), text, metadata or {}))
            st.success("🧠 문서 벡터 저장 완료!")
        except Exception as e:
            st.error(f"❌ 문서 벡터 저장 실패: {e}")

    def search(self, query: str, top_k: int = 5):
        try:
            query_emb = np.array(self.get_embedding(query)).reshape(1, -1)
            if not self.vectors:
                st.warning("⚠️ 저장된 문서 벡터가 없습니다.")
                return []

            doc_embeddings = np.array([vec[0] for vec in self.vectors])
            sims = cosine_similarity(query_emb, doc_embeddings)[0]
            top_indices = sims.argsort()[::-1][:top_k]

            results = []
            for idx in top_indices:
                emb, text, meta = self.vectors[idx]
                results.append({"text": text, "metadata": meta, "score": float(sims[idx])})

            return results
        except Exception as e:
            st.error(f"❌ 검색 실패: {e}")
            return []
