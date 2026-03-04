import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from scripts.build_email import build_email


def load_latest_output():
    path = "public/daily/latest.json"

    if not os.path.exists(path):
        raise Exception("latest.json not found")

    with open(path) as f:
        return json.load(f)


def send_email():

    api_key = os.getenv("SENDGRID_API_KEY")
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    dashboard_url = os.getenv("DASHBOARD_URL", "")

    if not api_key:
        raise Exception("SENDGRID_API_KEY missing")

    data = load_latest_output()

    subject, body = build_email(data)

    if dashboard_url:
        body += f"\n\nDashboard:\n{dashboard_url}"

    message = Mail(
        from_email=email_from,
        to_emails=email_to,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)

        print("EMAIL SENT SUCCESSFULLY")
        print("Status:", response.status_code)

    except Exception as e:
        print("EMAIL FAILED")
        print(e)
        raise e


if __name__ == "__main__":
    send_email()