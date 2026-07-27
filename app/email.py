import json
import pathlib
import asyncio
from typing import Optional, Dict
from pydantic import BaseModel
from app.config import settings

class EmailMessage(BaseModel):
    to: str
    subject: str
    html: str
    tags: Optional[Dict[str, str]] = None

def _dev_send(msg: EmailMessage) -> None:
    """
    Development email provider: outputs email to console and logs JSON record to logs/emails.log
    """
    print(f"[DEV EMAIL GATEWAY] To: {msg.to} | Subject: {msg.subject}")
    log_dir = pathlib.Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "emails.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(msg.model_dump()) + "\n")

async def _prod_send(msg: EmailMessage) -> None:
    """
    Production email provider stub (e.g. Resend / SendGrid REST client)
    """
    import httpx
    api_key = getattr(settings, "EMAIL_PROVIDER_KEY", "")
    if not api_key:
        _dev_send(msg)
        return

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": "no-reply@eventify.com",
                "to": msg.to,
                "subject": msg.subject,
                "html": msg.html
            },
            timeout=5.0
        )
        response.raise_for_status()

async def send_email(msg: EmailMessage) -> None:
    """
    Dispatches transactional emails asynchronously without blocking caller thread.
    """
    if settings.APP_ENV == "production":
        await _prod_send(msg)
    else:
        # Run dev logger in async loop
        await asyncio.to_thread(_dev_send, msg)
