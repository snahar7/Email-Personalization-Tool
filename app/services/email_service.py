"""AI email personalization (OpenAI) and SMTP sending."""
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from typing import Dict, Optional, Tuple

from openai import OpenAI

from app.models.models import Company, EmailTemplate, Prospect

DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are an expert B2B sales email writer. Write short, specific, "
    "personalized outreach emails with one clear call to action."
)


class ConfigError(RuntimeError):
    """Raised when a required env var (OpenAI key, SMTP settings) is missing."""


def get_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ConfigError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key)


def build_prompt(
    prospect: Prospect,
    company: Optional[Company],
    template: Optional[EmailTemplate] = None,
    additional_context: Optional[Dict] = None,
) -> str:
    c = company
    lines = [
        "Write a personalized cold email for this prospect.",
        "",
        "Prospect:",
        f"- Name: {prospect.name}",
        f"- Title: {prospect.position or 'unknown'}",
        f"- Notes: {prospect.notes or 'none'}",
        "",
        "Prospect's company:",
        f"- Name: {c.name if c else 'unknown'}",
        f"- Industry: {(c.industry if c else None) or 'unknown'}",
        f"- Description: {(c.description if c else None) or 'none'}",
        f"- Key insights: {(c.key_insights if c else None) or 'none'}",
        f"- Product info: {(c.product_info if c else None) or 'none'}",
        f"- Market position: {(c.market_position if c else None) or 'none'}",
    ]
    if template:
        lines += ["", "Base template to personalize:", f"Subject: {template.subject}", f"Body: {template.body}"]
    if additional_context:
        lines += ["", "Additional context (e.g. product usage):"]
        lines += [f"- {k}: {v}" for k, v in additional_context.items()]
    lines += [
        "",
        "Reply in exactly this format:",
        "SUBJECT: <subject line>",
        "BODY:",
        "<email body>",
    ]
    return "\n".join(lines)


def parse_email(content: str) -> Tuple[str, str]:
    subject, body_lines, in_body = "", [], False
    for line in content.strip().splitlines():
        if not in_body and line.upper().startswith("SUBJECT:"):
            subject = line.split(":", 1)[1].strip()
        elif not in_body and line.upper().startswith("BODY:"):
            in_body = True
            rest = line.split(":", 1)[1].strip()
            if rest:
                body_lines.append(rest)
        elif in_body:
            body_lines.append(line)
    if not in_body:  # model ignored the format; use everything as body
        body_lines = [l for l in content.strip().splitlines() if not l.upper().startswith("SUBJECT:")]
    return subject, "\n".join(body_lines).strip()


def generate_personalized_email(
    prospect: Prospect,
    company: Optional[Company],
    template: Optional[EmailTemplate] = None,
    additional_context: Optional[Dict] = None,
    client: Optional[OpenAI] = None,
) -> Dict:
    client = client or get_openai_client()
    model = get_model()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(prospect, company, template, additional_context)},
        ],
        temperature=0.7,
        max_tokens=800,
    )
    subject, body = parse_email(response.choices[0].message.content or "")
    return {
        "subject": subject,
        "body": body,
        "model": model,
        "generated_at": datetime.now(timezone.utc),
    }


def smtp_configured() -> bool:
    return all(os.getenv(k) for k in ("SMTP_SERVER", "SMTP_USERNAME", "SMTP_PASSWORD"))


def send_email(to: str, subject: str, body: str) -> None:
    if not smtp_configured():
        raise ConfigError("SMTP_SERVER, SMTP_USERNAME and SMTP_PASSWORD must be set to send email")
    msg = EmailMessage()
    msg["From"] = os.getenv("SMTP_FROM", os.environ["SMTP_USERNAME"])
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    port = int(os.getenv("SMTP_PORT", "587"))
    with smtplib.SMTP(os.environ["SMTP_SERVER"], port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)
