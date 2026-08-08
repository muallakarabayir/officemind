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
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

def chunk_markdown(text: str, source: str) -> list[dict]:
    """
    Markdown dosyasını ## başlıklarına göre parçalara böler.
    Her chunk için hem 'orijinal metin' (gösterim için) hem de
    'embed edilecek metin' (bağlam eklenmiş) ayrı tutulur.
    """
    # Dokümanın genel başlığını (# ile başlayan) al
    title_match = re.match(r"^#\s+(.+)", text)
    doc_title = title_match.group(1) if title_match else source

    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^##\s+(.+)", section)
        heading = heading_match.group(1) if heading_match else "Giriş"

        # Embed edilecek metne bağlam ekle (contextual chunking)
        context_prefix = f"Doküman: {doc_title}. Bölüm: {heading}.\n"
        embed_text = context_prefix + section

        chunks.append({
            "text": section,          # gösterim için orijinal metin
            "embed_text": embed_text, # embedding için bağlamlı metin
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
    texts = [c["embed_text"] for c in all_chunks]   # değişiklik burada: embed_text kullan
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