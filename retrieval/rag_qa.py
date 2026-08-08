"""
RAG Soru-Cevap scripti: Hibrit arama (search.py) ile en alakalı chunk'ları
bulur, bunları Gemini'ye bağlam olarak verir ve kaynak referanslı,
doğal bir cevap ürettirir.


"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from search import search  # aynı klasördeki search.py'den hibrit arama fonksiyonu

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-flash-latest"  # her zaman güncel/desteklenen Flash modelini işaret eder

SYSTEM_PROMPT = """Sen TechCorp şirketinin iç bilgi asistanısın. Sana verilen doküman
parçalarına dayanarak çalışanların sorularını cevaplıyorsun.

Kurallar:
- SADECE sana verilen doküman parçalarındaki bilgiyi kullan, kendi bilgini asla ekleme.
- Cevabının sonunda hangi dokümandan/dokümanlardan yararlandığını mutlaka belirt.
- Eğer verilen doküman parçalarında sorunun cevabı yoksa, açıkça "Bu konuda
  dokümanlarımda bilgi bulamadım" de. Asla tahmin yürütme veya uydurma.
- Kısa, net ve profesyonel bir dille cevap ver.
"""


def build_context(chunks) -> str:
    """Retrieval sonuçlarını modele verilecek bağlam metnine çevirir."""
    parts = []
    for i, (final_score, sem, kw, hit) in enumerate(chunks, 1):
        parts.append(
            f"[Doküman {i} - Kaynak: {hit.payload['source']} - "
            f"Bölüm: {hit.payload['heading']}]\n{hit.payload['text']}"
        )
    return "\n\n".join(parts)


def ask(question: str) -> str:
    # 1. Hibrit arama ile en alakalı chunk'ları bul (ekrana yazdırmadan)
    chunks = search(question, top_k=5)

    if not chunks:
        return "Bu konuda dokümanlarımda bilgi bulamadım."

    context = build_context(chunks)
    user_content = f"Doküman parçaları:\n\n{context}\n\nSoru: {question}"

    # 2. Gemini'ye sistem talimatı + bağlam + soruyu gönder
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
    )

    return response.text


if __name__ == "__main__":
    test_questions = [
        "İzin hakkım nedir?",
        "VPN nasıl kurulur?",
        "Şifremi unuttum ne yapmalıyım?",
        "Maaş zammı ne zaman olur?",  # dokümanlarda olmayan bir soru - halüsinasyon testi
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"❓ Soru: {q}\n")
        answer = ask(q)
        print(f"💬 Cevap:\n{answer}")