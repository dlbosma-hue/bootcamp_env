import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SCORE_THRESHOLDS


def _build_html(apply: list[dict], maybe: list[dict], total_seen: int, total_new: int) -> str:
    today = date.today().strftime("%d %b %Y")

    def job_block(job: dict, colour: str) -> str:
        return f"""
        <tr>
          <td style="padding:12px 0; border-bottom:1px solid #eee;">
            <span style="font-size:18px;">{colour}</span>
            <strong style="font-size:15px;">{job['title']}</strong>
            — {job['company']}, {job['location']}<br>
            <span style="color:#555; font-size:13px;">{job['match_reason']}</span><br>
            <a href="{job['url']}" style="font-size:13px; color:#0066cc;">View job →</a>
            &nbsp;&nbsp;<span style="background:#f0f0f0; padding:2px 8px; border-radius:10px;
              font-size:12px;">Score: {job['score']}/10 · {job['source']}</span>
          </td>
        </tr>"""

    apply_rows = "".join(job_block(j, "🟢") for j in apply) or "<tr><td style='color:#888;padding:8px 0;'>No top matches today.</td></tr>"
    maybe_rows = "".join(job_block(j, "🟡") for j in maybe) or "<tr><td style='color:#888;padding:8px 0;'>No borderline matches today.</td></tr>"

    return f"""
    <html><body style="font-family:Arial,sans-serif; max-width:680px; margin:0 auto; color:#333;">
      <h2 style="color:#1a1a2e;">📋 Weekly Job Digest — {today}</h2>
      <p style="color:#666; font-size:13px;">{total_new} new jobs found · {total_seen} already seen and skipped</p>

      <h3 style="color:#2d6a4f;">🟢 Apply (score {SCORE_THRESHOLDS['apply']}–10)</h3>
      <table width="100%" cellpadding="0" cellspacing="0">{apply_rows}</table>

      <h3 style="color:#b5882e; margin-top:24px;">🟡 Maybe (score {SCORE_THRESHOLDS['maybe']}–{SCORE_THRESHOLDS['apply']-1})</h3>
      <table width="100%" cellpadding="0" cellspacing="0">{maybe_rows}</table>

      <p style="color:#aaa; font-size:11px; margin-top:32px;">
        Sources: LinkedIn · Indeed · Glassdoor · Stepstone · Jobs older than 7 days excluded.
      </p>
    </body></html>
    """


def send_digest(scored_jobs: list[dict], total_fetched: int, already_seen: int) -> None:
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    recipients = [r.strip() for r in os.environ["EMAIL_RECIPIENT"].split(",")]

    apply = sorted(
        [j for j in scored_jobs if j.get("score", 0) >= SCORE_THRESHOLDS["apply"]],
        key=lambda x: x["score"], reverse=True,
    )
    maybe = sorted(
        [j for j in scored_jobs if SCORE_THRESHOLDS["maybe"] <= j.get("score", 0) < SCORE_THRESHOLDS["apply"]],
        key=lambda x: x["score"], reverse=True,
    )

    total_notified = len(apply) + len(maybe)
    if total_notified == 0:
        print("[notifier] No matches above threshold — skipping email.")
        return

    today = date.today().strftime("%d %b %Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Weekly Job Digest {today} — {len(apply)} apply, {len(maybe)} maybe"
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    html = _build_html(apply, maybe, already_seen, total_fetched)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipients, msg.as_string())

    print(f"[notifier] Email sent to {recipients}: {len(apply)} apply, {len(maybe)} maybe")
