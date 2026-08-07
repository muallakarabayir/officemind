"""
İlk ingestion scripti: data/sample_docs/ altındaki .md dosyalarını okur,
başlıklara göre parçalara (chunk) böler, embedding üretir ve Qdrant'a yükler.
"""

import os
import glob
import re
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# --- Ayarlar ---
DOCS_PATH = "data/sample_docs/*.md"
COLLECTION_NAME = "techcorp_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # küçük, hızlı, lokal çalışan model

def chunk_markdown(text: str, source: str) -> list[dict]:
    """
    Markdown dosyasını ## başlıklarına göre parçalara böler.
    Her chunk bir sözlük olarak döner: {"text": ..., "source": ..., "heading": ...}
    """
    # ## ile başlayan başlıklardan böl
    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Başlığı ayıkla (varsa)
        heading_match = re.match(r"^##\s+(.+)", section)
        heading = heading_match.group(1) if heading_match else "Giriş"
        chunks.append({
            "text": section,
            "source": source,
            "heading": heading
        })
    return chunks


def main():
    print("Embedding modeli yükleniyor...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Qdrant'a bağlanılıyor...")
    client = QdrantClient(host="localhost", port=6333)

    # Koleksiyon oluştur (zaten varsa siler, temiz baştan kurar)
    vector_size = model.get_sentence_embedding_dimension()
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    all_chunks = []
    for filepath in glob.glob(DOCS_PATH):
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        doc_chunks = chunk_markdown(text, source=filename)
        all_chunks.extend(doc_chunks)
        print(f"  {filename}: {len(doc_chunks)} chunk bulundu")

    print(f"\nToplam {len(all_chunks)} chunk embed ediliyor...")
    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    points = []
    for idx, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
        points.append(PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "text": chunk["text"],
                "source": chunk["source"],
                "heading": chunk["heading"]
            }
        ))

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"\n✅ Tamamlandı! {len(points)} chunk Qdrant'a yüklendi.")
    print(f"Dashboard'da kontrol edebilirsin: http://localhost:6333/dashboard")


if __name__ == "__main__":
    main()