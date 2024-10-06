import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(subject, message, to_email):
    message = Mail(
        from_email=os.environ.get("DEFAULT_FROM_EMAIL"),
        to_emails=to_email,
        subject=subject,
        html_content=message
    )

    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        print(f"An error occurred while sending email to {to_email}. {e}")