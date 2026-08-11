"""
Niyet Tespiti (Intent Classification): Kullanıcının mesajını 4 kategoriden
birine ayırır. Bu, agent'ın "ne yapması gerektiğine" karar verdiği ilk adımdır.

Kategoriler:
- bilgi_sorgusu: Kullanıcı bir şey soruyor, RAG ile cevaplanabilir
- eylem_talebi: Kullanıcı bir işlem yapılmasını istiyor (ticket, e-posta vb.)
- sohbet: Selamlaşma, teşekkür, küçük konuşma - RAG'a gerek yok
- belirsiz: Niyet net değil, netleştirme sorusu gerekir
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-flash-lite-latest" # her zaman güncel/desteklenen Flash modelini işaret eder

VALID_CATEGORIES = {"bilgi_sorgusu", "eylem_talebi", "sohbet", "belirsiz"}

CLASSIFIER_PROMPT = """Sen bir niyet sınıflandırma sistemisin. Kullanıcının TechCorp
şirket asistanına yazdığı mesajı analiz et ve SADECE aşağıdaki 4 kategoriden
birini, başka hiçbir şey yazmadan döndür:

- bilgi_sorgusu: Kullanıcı bir bilgi/politika/prosedür soruyor (örn. "izin hakkım nedir", "VPN nasıl kurulur")
- eylem_talebi: Kullanıcı bir işlem yapılmasını istiyor - ticket açma, e-posta gönderme, bir sorunu bildirme (örn. "bilgisayarım açılmıyor", "bu dokümanı ekibe mail at", "yardım lazım")
- sohbet: Selamlaşma, teşekkür, veda, küçük konuşma (örn. "merhaba", "teşekkürler", "naber")
- belirsiz: Mesaj çok kısa/anlamsız veya niyet hiç net değil

SADECE kategori adını yaz, başka hiçbir açıklama, noktalama veya tırnak işareti ekleme.

Kullanıcı mesajı: "{message}"

Kategori:"""


def _parse_category(raw_text: str) -> str:
    """
    Modelin döndürdüğü ham metinden kategori adını ayıklar.
    Model bazen fazladan boşluk, tırnak veya noktalama ekleyebiliyor,
    bu yüzden hem tam eşleşme hem de "içinde geçme" kontrolü yapıyoruz.
    """
    raw = raw_text.strip().lower()

    # 1. Önce fazlalıkları temizleyip tam eşleşme dene
    cleaned = raw.strip(" \"'.:\n")
    if cleaned in VALID_CATEGORIES:
        return cleaned

    # 2. Tam eşleşme yoksa, ham metnin içinde geçen kategori adını ara
    for category in VALID_CATEGORIES:
        if category in raw:
            return category

    # 3. Hiçbiri uymuyorsa güvenli tarafta kal
    return "belirsiz"


def classify_intent(message: str) -> str:
    """Mesajı 4 kategoriden birine sınıflandırır, kategori adını döner."""
    prompt = CLASSIFIER_PROMPT.format(message=message)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=200,  # düşünme token'larına da yer bırakmak için yüksek tutuyoruz
        ),
    )

    if response.text is None:
        return "belirsiz"

    return _parse_category(response.text)


if __name__ == "__main__":
    test_messages = [
        "İzin hakkım nedir?",
        "VPN nasıl kurulur?",
        "Bilgisayarım açılmıyor, yardım lazım",
        "Bu dokümanı ekibe mail at",
        "Merhaba, nasılsın?",
        "Teşekkürler!",
        "asdfghjkl",
    ]

    for msg in test_messages:
        intent = classify_intent(msg)
        print(f"Mesaj: {msg}\n-> Niyet: {intent}\n")