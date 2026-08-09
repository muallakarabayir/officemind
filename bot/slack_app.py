
"""
Slack Bot: OfficeMind'ı Slack'e bağlayan ana dosya.
Bot mention edildiğinde veya kendisine DM atıldığında,
retrieval/rag_qa.py'deki RAG motorunu kullanarak cevap verir.
"""


import os 
import sys
import re
from xml.sax import handler


from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

#retrieval/ klasorunu Python un arama yoluna ekle, boylece rag_qa ve search modüllerini import edebiliriz
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "retrieval"))

from rag_qa import ask

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

def clean_mention_text(text: str) -> str:
    """Slack'teki bot mention'ını temizler, sadece soruyu bırakır."""
    return re.sub(r"<@[A-Z0-9]+>", "", text).strip()

@app.event("app_mention")
def handle_mention(event, say):
    """Bot bir kanalda @mention edildiginde tetilenir."""
    question = clean_mention_text(event.get("text", ""))

    if not question:
        say("Merhaba! Bana bir soru sormak için mesajına sorunu yazabilirsin.")
        return

    say("Bakiyorum...", thread_ts=event["ts"])
    answer = ask(question)
    say(answer, thread_ts=event["ts"])


@app.event("message")
def handle_direct_message(event, say):
    """Bota direkt meaj (DM) atıldığında tetilenir."""
    #Kanal tipi 'im' değilse, bu bir DM değil, başka bir kanal mesajıdır, o yüzden ignore et
    if event.get("channel_type") != "im":
        return
    #Botun kendi mesajlarini yoksay(sonsuz dongu olamsin)
    if event.get("bot_id"):
        return


    question = event.get("text", "").strip()
    if not question:
        return

    say("Bakiyorum...")
    answer = ask(question)
    say(answer)


if __name__ == "__main__":
    print("OfficeMind Slack botu başlatılıyor...")
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()

