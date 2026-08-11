"""
Geçici script: Bu API key ile hangi Gemini modellerinin kullanılabilir
olduğunu listeler. Sorunu çözdükten sonra bu dosyayı silebilirsin.
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

print("Kullanılabilir modeller (generateContent destekleyenler):\n")
for model in client.models.list():
    if "generateContent" in (model.supported_actions or []):
        print(f"- {model.name}")