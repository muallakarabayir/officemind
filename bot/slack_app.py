"""
Slack Bot: OfficeMind'ı Slack'e bağlayan ana dosya.
Artık her mesajı önce niyet tespitinden (agent/intent_classifier.py)
geçiriyor, sonra niyete göre uygun davranışı seçiyor:

- bilgi_sorgusu -> RAG motoruyla (retrieval/rag_qa.py) cevap üretir
- eylem_talebi  -> şimdilik "bu özellik yakında geliyor" der (Faz 4'te gerçek ticket/e-posta eklenecek)
- sohbet        -> API çağırmadan, hazır bir selamlaşma/teşekkür cevabı verir (kota tasarrufu)
- belirsiz      -> netleştirici bir soru sorar
"""

import os
import sys
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# retrieval/ ve agent/ klasörlerini Python'un arama yoluna ekle
BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(BASE_DIR, "..", "retrieval"))
sys.path.insert(0, os.path.join(BASE_DIR, "..", "agent"))

from rag_qa import ask  # noqa: E402
from intent_classifier import classify_intent  # noqa: E402

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# "sohbet" niyeti için API çağırmadan verilecek hazır cevaplar (kota tasarrufu)
SOHBET_CEVAPLARI = {
    "selam": "Merhaba! 👋 Sana nasıl yardımcı olabilirim? Örneğin 'İzin hakkım nedir?' gibi bir soru sorabilirsin.",
    "tesekkur": "Rica ederim! Başka bir sorun olursa buradayım. 🙂",
    "varsayilan": "Merhaba! Ben OfficeMind, TechCorp'un iç bilgi asistanıyım. Politikalar, IT prosedürleri gibi konularda sana yardımcı olabilirim.",
}


def clean_mention_text(text: str) -> str:
    """Mesajdaki '<@BOT_ID>' gibi mention etiketlerini temizler."""
    return re.sub(r"<@[A-Z0-9]+>", "", text).strip()


def pick_sohbet_cevabi(message: str) -> str:
    """Sohbet niyeti için mesaj içeriğine göre uygun hazır cevabı seçer."""
    lower = message.lower()
    if any(word in lower for word in ["teşekkür", "sağol", "sağ ol", "eyvallah"]):
        return SOHBET_CEVAPLARI["tesekkur"]
    if any(word in lower for word in ["merhaba", "selam", "naber", "günaydın", "iyi günler"]):
        return SOHBET_CEVAPLARI["selam"]
    return SOHBET_CEVAPLARI["varsayilan"]


def route_message(message: str) -> str:
    """
    Mesajı niyet tespitinden geçirir ve uygun cevabı üretir.
    Bu fonksiyon, agent'ın 'karar verme' katmanının kalbidir.
    """
    if not message:
        return SOHBET_CEVAPLARI["varsayilan"]

    intent = classify_intent(message)

    if intent == "sohbet":
        return pick_sohbet_cevabi(message)

    if intent == "bilgi_sorgusu":
        return ask(message)

    if intent == "eylem_talebi":
        return (
            "Bu bir eylem talebi gibi görünüyor (örn. ticket açma, e-posta gönderme). "
            "Bu özellik henüz geliştirme aşamasında (Faz 4), ama yakında ekleniyor! 🚧\n\n"
            "Şimdilik sana bu konuda dokümanlardan bilgi bulmayı deneyebilirim, istersen "
            "sorunu biraz daha detaylandırır mısın?"
        )

    # belirsiz
    return (
        "Tam olarak ne demek istediğini anlayamadım. 🤔\n"
        "Bana bir şey mi sormak istiyorsun, yoksa bir işlem mi yapmamı istiyorsun? "
        "Biraz daha detay verirsen yardımcı olabilirim."
    )


@app.event("app_mention")
def handle_mention(event, say):
    """Bot bir kanalda @mention edildiğinde tetiklenir."""
    question = clean_mention_text(event.get("text", ""))
    say("🔍 Bakıyorum...", thread_ts=event.get("ts"))
    answer = route_message(question)
    say(text=answer, thread_ts=event.get("ts"))


@app.event("message")
def handle_direct_message(event, say):
    """Bota direkt mesaj (DM) atıldığında tetiklenir."""
    if event.get("channel_type") != "im":
        return
    if event.get("bot_id"):
        return

    question = event.get("text", "").strip()
    if not question:
        return

    say("🔍 Bakıyorum...")
    answer = route_message(question)
    say(answer)


if __name__ == "__main__":
    print("🤖 OfficeMind Slack botu başlatılıyor (niyet tespiti aktif)...")
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()