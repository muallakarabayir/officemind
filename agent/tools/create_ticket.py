"""
Jira Ticket Açma Aracı: Agent'ın "eylem_talebi" niyeti tespit ettiğinde
kullanacağı araçlardan biri. Verilen başlık/açıklamayla Jira'da yeni
bir issue (ticket) oluşturur.
 
Gerekli .env değişkenleri:
- JIRA_SITE_URL: örn. https://techcorp-mualla.atlassian.net
- JIRA_EMAIL: Jira hesabının bağlı olduğu e-posta
- JIRA_API_TOKEN: id.atlassian.com/manage-profile/security/api-tokens'tan alınan token
- JIRA_PROJECT_KEY: örn. "OD" (proje oluşturulunca otomatik üretilen kısaltma)
"""



from asyncio import Task
import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_SITE_URL = os.getenv("JIRA_SITE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")


def create_ticket(title: str, description: str, priority: str = "Medium") -> str:
    """
    Jira'da yeni bir issue olusturur.

    Doner:
    {"success": True, "ticket_key": "OD-123"} 
    veya 
    {"success": False, "error": "Hata mesajı"}
    """
    if not all ([JIRA_SITE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
        return {
                "success": False, 
                "error": "Jira ayarları eksik. .env dosyasını kontrol et."
                "JIRA_SITE_URL, JIRA_EMAIL, JIRA_API_TOKEN ve JIRA_PROJECT_KEY değişkenleri gerekli."
                }

    url = f"{JIRA_SITE_URL}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            },
            "issuetype": {"name": "Task"},
        }
    }

    try:
        response = requests.post(
            url,
            json = payload,
            auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN),
            headers={"Content-Type": "application/json"},
            timeout=10  # 10 saniye timeout
        )
        response.raise_for_status()  # HTTP hatalarını tetikler
        data = response.json()
        ticket_key = data.get("key")
        ticket_url = f"{JIRA_SITE_URL}/browse/{ticket_key}"
        return {"success": True, "ticket_key": ticket_key, "ticket_url": ticket_url}

    except requests.exceptions.RequestException as e:
        return { "success": False, "error": f"Jira API hatasi : {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Bağlantı hatası: {str(e)}"}


if __name__ == "__main__":
    # Test: gerçek bir ticket açar (Jira kimlik bilgileri .env'de olmalı)
    result = create_ticket(
        title="[TEST] Bilgisayar açılmıyor",
        description="Bu, OfficeMind botunun otomatik ticket açma özelliğini test etmek için oluşturulmuş bir test ticket'ıdır.",
    )
    print(result)