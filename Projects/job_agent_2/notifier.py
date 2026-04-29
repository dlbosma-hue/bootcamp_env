import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import MIN_EMAIL_SCORE


def _section_html(jobs: list[dict], flag: str, label: str, score_range: str) -> str:
    relevant = [j for j in jobs if j["flag"] == flag]
    if not relevant:
        return ""
    rows = ""
    for i, j in enumerate(relevant, 1):
        rows += f"""
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #eee;vertical-align:top;">
            <strong>{i}. {j['title']}</strong> — {j['company']}, {j['location']}<br>
            <span style="color:#555;">Score: {j['score']}/10 &nbsp;|&nbsp; {j['match_reason']}</span><br>
            <a href="{j['url']}" style="color:#1a73e8;">View job →</a>
          </td>
        </tr>"""
    return f"""
    <tr><td style="padding:16px 0 4px;"><strong>{label}&nbsp;&nbsp;
      <span style="color:#888;font-weight:normal;font-size:13px;">(score {score_range})</span>
    </strong></td></tr>
    <tr><td><table width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>"""


def send_digest(jobs_scored: list[dict], total_seen: int) -> None:
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_PASSWORD"]
    recipients = [r.strip() for r in os.environ["EMAIL_TO"].split(",")]
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    # Only email jobs above the threshold
    email_jobs = [j for j in jobs_scored if j["score"] >= MIN_EMAIL_SCORE]

    n_apply = sum(1 for j in email_jobs if j["flag"] == "apply")
    n_maybe = sum(1 for j in email_jobs if j["flag"] == "maybe")
    n_skipped = total_seen - len(email_jobs)

    date_str = datetime.now().strftime("%a %-d %b %Y")
    subject = (
        f"Job Digest — {date_str}"
        f" | {n_apply} to apply"
        + (f", {n_maybe} maybe" if n_maybe else "")
    )

    apply_section = _section_html(email_jobs, "apply", "✅ APPLY",  "8–10")
    maybe_section = _section_html(email_jobs, "maybe", "🤔 MAYBE",  "6–7")

    if not apply_section and not maybe_section:
        body_content = "<p style='color:#888;'>No strong matches today. Check back tomorrow.</p>"
    else:
        body_content = f"""
        <table width="100%" cellpadding="0" cellspacing="0">
          {apply_section}
          {maybe_section}
          <tr><td style="padding:20px 0 0;border-top:2px solid #eee;color:#888;font-size:12px;">
            {total_seen} jobs seen today — {n_skipped} skipped (already seen or score &lt; {MIN_EMAIL_SCORE})
          </td></tr>
        </table>"""

    html = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:680px;margin:0 auto;color:#222;">
      <h2 style="border-bottom:2px solid #1a73e8;padding-bottom:8px;">
        Job Digest &mdash; {date_str}
      </h2>
      {body_content}
    </body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"[notifier] Email sent: '{subject}' → {recipients}")
