import httpx
from app.core.config import settings


class DingTalkBotService:
    """DingTalk bot webhook service."""

    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or settings.DINGTALK_WEBHOOK_URL

    async def send_text(self, message: str) -> dict:
        if not self.webhook_url:
            return {"ok": False, "error": "DINGTALK_WEBHOOK_URL not configured"}
        payload = {"msgtype": "text", "text": {"content": message}}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload, timeout=10.0)
            return response.json()

    async def send_markdown(self, title: str, text: str) -> dict:
        if not self.webhook_url:
            return {"ok": False, "error": "DINGTALK_WEBHOOK_URL not configured"}
        payload = {"msgtype": "markdown", "markdown": {"title": title, "text": text}}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload, timeout=10.0)
            return response.json()
