
"""
E-posta Gönderme Aracı: Agent'ın "eylem_talebi" niyeti tespit ettiğinde
kullanacağı araçlardan biri. Gmail SMTP (Uygulama Şifresi ile) üzerinden
e-posta gönderir.
 
Gerekli .env değişkenleri:
- GMAIL_ADDRESS: gönderen Gmail adresi, örn. officemind.bot@gmail.com
- GMAIL_APP_PASSWORD: Google hesap ayarlarından oluşturulan 16 haneli
  "Uygulama Şifresi" (normal Gmail şifresi DEĞİL)
 
Uygulama Şifresi almak için:
  myaccount.google.com/apppasswords adresinden oluşturulabilir
  (2 Adımlı Doğrulama açık olmalı).
"""

import os 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # TLS portu

def send_email(to: str, subject: str, body: str) -> dict:
    """
    Gmail SMTP üzerinden e-posta gönderir.

    Doner:
    {"success": True} veya {"success": False, "error": "Hata mesajı"}
    """
    if not all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD]):
        return{ 
            "success": False,
            "error":" Gmail ayarları eksik. .env dosyasını kontrol et. GMAIL_ADDRESS ve GMAIL_APP_PASSWORD değişkenleri gerekli."
            "GMAIL_ADDRESS ve GMAIL_APP_PASSWORD değişkenleri gerekli."
        }

    message = MIMEMultipart()
    message["From"] = GMAIL_ADDRESS
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS şifrelemesini başlat
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to, message.as_string())
        return {"success": True}

    except smtplib.SMTPAuthenticationError:
        return{
            "success": False,
            "error": "Gmail kimlik dogrulama hatasi. Uygulama Sifresi dogru mu kontrol et."

        }
    except Exception as e:
        return{
            "success":False, "error": f" Eposta gonderilemedi: {str(e)}"
    
        }

if __name__ == "__main__":
    # Test: gerçek bir e-posta gönderir (Gmail kimlik bilgileri .env'de olmalı)
    result = send_email(
        to="mualla.krbyr@gmail.com",  # buraya kendi test e-postanı yaz
        subject="[TEST] OfficeMind Bot Testi",
        body="Bu, OfficeMind botunun otomatik e-posta gönderme özelliğini test etmek için gönderilmiş bir test mesajıdır.",
    )
    print(result)