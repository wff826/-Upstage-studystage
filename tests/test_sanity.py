import os
import pytest
from upstage import UpstageEmbeddings
from services.parse import parse_document
from services.vectorstore import get_vectorstore

# 테스트용 샘플 파일 경로
TEST_FILE = "tests/sample_docs/sample.pdf"

@pytest.mark.parametrize("filepath", [TEST_FILE])
def test_document_parsing(filepath):
    """문서 파싱이 정상적으로 되는지 확인"""
    assert os.path.exists(filepath), "❌ 테스트 파일이 존재하지 않습니다."

    # 1. 문서 파싱
    docs = parse_document(filepath)
    assert len(docs) > 0, "❌ 문서에서 추출된 내용이 없습니다."
    print(f"✅ 문서에서 {len(docs)} chunk 추출됨")

    # 2. OCR/텍스트 길이 확인
    total_text = " ".join([d.page_content for d in docs])
    assert len(total_text) > 50, "❌ 추출된 텍스트가 너무 짧습니다. (OCR 실패 가능성)"
    print(f"✅ 추출된 텍스트 길이: {len(total_text)}자")

def test_vectorstore_indexing():
    """파싱된 문서가 벡터스토어에 잘 들어갔는지 확인"""
    docs = parse_document(TEST_FILE)
    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
    vectorstore = get_vectorstore(docs, embeddings)
