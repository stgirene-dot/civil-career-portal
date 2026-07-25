import html
import json
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTAL_URL = "https://stgirene-dot.github.io/civil-career-portal/"


def required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required GitHub Actions secret: {name}")
    return value


def build_content(jobs, is_test):
    if is_test:
        return (
            "Civil Career Portal email test",
            "Email notifications are configured correctly. Future messages will only be sent when a new opportunity is discovered.",
            f"<p>Email notifications are configured correctly.</p><p>Future messages will only be sent when a new opportunity is discovered.</p><p><a href=\"{PORTAL_URL}\">Open Civil Career Portal</a></p>",
        )

    count = len(jobs)
    subject = f"{count} new career opportunit{'y' if count == 1 else 'ies'}"
    text_parts = [f"{subject} found by Civil Career Portal:\n"]
    html_parts = [f"<h2>{html.escape(subject)}</h2>"]
    for job in jobs:
        title = job.get("englishTitle") or job.get("title") or "New opportunity"
        location = job.get("location") or job.get("country") or "Asia"
        institution = job.get("institution") or ""
        url = job.get("url") or PORTAL_URL
        text_parts.append(f"{title}\n{institution} · {location}\n{url}\n")
        html_parts.append(
            "<article style=\"margin:0 0 20px\">"
            f"<h3>{html.escape(title)}</h3>"
            f"<p>{html.escape(institution)} · {html.escape(location)}</p>"
            f"<p><a href=\"{html.escape(url, quote=True)}\">View official posting</a></p>"
            "</article>"
        )
    text_parts.append(f"Browse all matches: {PORTAL_URL}")
    html_parts.append(f"<p><a href=\"{PORTAL_URL}\">Browse all portal matches</a></p>")
    return subject, "\n".join(text_parts), "".join(html_parts)


def send_email(sender, password, recipient, subject, text_body, html_body):
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(sender, password)
        smtp.send_message(message)


def main():
    is_test = os.environ.get("SEND_TEST_NOTIFICATION", "false").lower() == "true"
    jobs_path = ROOT / ".new-jobs.json"
    jobs = json.loads(jobs_path.read_text()) if jobs_path.exists() else []
    if not jobs and not is_test:
        print("No new opportunities; no email sent.")
        return

    sender = required_env("GMAIL_ADDRESS")
    password = required_env("GMAIL_APP_PASSWORD")
    recipients = [
        address.strip()
        for address in required_env("NOTIFICATION_RECIPIENTS").split(",")
        if address.strip()
    ]
    if not recipients:
        raise RuntimeError("NOTIFICATION_RECIPIENTS contains no email addresses")

    subject, text_body, html_body = build_content(jobs, is_test)
    for recipient in recipients:
        send_email(sender, password, recipient, subject, text_body, html_body)
    print(f"Sent notification to {len(recipients)} recipient(s).")


if __name__ == "__main__":
    main()
