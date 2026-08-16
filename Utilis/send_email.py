import resend
from django.conf import settings
import os
from dotenv import load_dotenv
load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to_email, subject, html):
    params = {
        "from": EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "html": html,
    }

    try:
        email = resend.Emails.send(params)
        return email
    except Exception as e:
        print("Resend Error:", e)
        return None