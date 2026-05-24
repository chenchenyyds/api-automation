import httpx
from app.core.config import settings


class FeishuBotService:
    """Feishu/Lark bot webhook service."""

    def __init__(self, webhook_url: str | None = None):
        self.webhook_url = webhook_url or settings.FEISHU_WEBHOOK_URL

    async def send_text(self, message: str) -> dict:
        if not self.webhook_url:
            return {"ok": False, "error": "FEISHU_WEBHOOK_URL not configured"}
        payload = {"msg_type": "text", "content": {"text": message}}
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload, timeout=10.0)
            return response.json()

    async def send_card(self, title: str, content: str) -> dict:
        if not self.webhook_url:
            return {"ok": False, "error": "FEISHU_WEBHOOK_URL not configured"}
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": title},
                    "template": "blue",
                },
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": content}}
                ],
            },
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.webhook_url, json=payload, timeout=10.0)
            return response.json()
