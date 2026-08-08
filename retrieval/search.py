"""
Hibrit retrieval scripti: semantik arama (embedding) + anahtar kelime
skorlaması (BM25) birleştirilerek daha isabetli sonuçlar üretir.
"""

import re
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from rank_bm25 import BM25Okapi

COLLECTION_NAME = "techcorp_docs"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 3
CANDIDATE_POOL = 15  # önce daha geniş bir havuz çekilir, sonra yeniden sıralanır
SEMANTIC_WEIGHT = 0.6
KEYWORD_WEIGHT = 0.4


def tokenize(text: str) -> list[str]:
    # basit Türkçe uyumlu tokenizasyon: küçük harfe çevir, kelimelere böl
    return re.findall(r"\w+", text.lower())


def normalize(scores: list[float]) -> list[float]:
    if not scores:
        return scores
    max_s, min_s = max(scores), min(scores)
    if max_s == min_s:
        return [1.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]


def search(query: str, top_k: int = TOP_K):
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(host="localhost", port=6333)

    # 1. Semantik arama: geniş bir aday havuzu çek
    query_vector = model.encode(query).tolist()
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=CANDIDATE_POOL,
    )
    candidates = response.points

    if not candidates:
        print("Sonuç bulunamadı.")
        return []

    # 2. BM25 ile anahtar kelime skorlaması (sadece bu adaylar üzerinde)
    tokenized_corpus = [tokenize(hit.payload["text"]) for hit in candidates]
    bm25 = BM25Okapi(tokenized_corpus)
    keyword_scores = bm25.get_scores(tokenize(query))

    # 3. Skorları normalize edip ağırlıklı birleştir
    semantic_scores = [hit.score for hit in candidates]
    norm_semantic = normalize(semantic_scores)
    norm_keyword = normalize(list(keyword_scores))

    combined = []
    for hit, sem, kw in zip(candidates, norm_semantic, norm_keyword):
        final_score = SEMANTIC_WEIGHT * sem + KEYWORD_WEIGHT * kw
        combined.append((final_score, sem, kw, hit))

    # 4. Birleşik skora göre yeniden sırala, ilk top_k'yı al
    combined.sort(key=lambda x: x[0], reverse=True)
    top_results = combined[:top_k]

    print(f"\n🔍 Soru: {query}\n")
    print(f"En alakalı {len(top_results)} chunk (hibrit skor):\n")

    for i, (final_score, sem, kw, hit) in enumerate(top_results, 1):
        print(f"--- Sonuç {i} (birleşik: {final_score:.3f} | semantik: {sem:.3f} | kelime: {kw:.3f}) ---")
        print(f"Kaynak: {hit.payload['source']} | Başlık: {hit.payload['heading']}")
        print(hit.payload["text"][:300] + "...")
        print()

    return top_results


if __name__ == "__main__":
    test_questions = [
        "İzin hakkım nedir?",
        "VPN nasıl kurulur?",
        "Şifremi unuttum ne yapmalıyım?",
    ]

    for q in test_questions:
        search(q)
        print("=" * 60)