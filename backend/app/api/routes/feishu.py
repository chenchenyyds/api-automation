from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.models import Message
from app.services.feishu import FeishuBotService

router = APIRouter(prefix="/feishu", tags=["feishu-webhook"])


class TextMessage(BaseModel):
    message: str


class CardMessage(BaseModel):
    title: str
    content: str


@router.post("/test", response_model=Message)
async def feishu_test() -> Any:
    """Send a test message to Feishu."""
    service = FeishuBotService()
    result = await service.send_text("Test message from API Automation Service.")
    return Message(message=f"Feishu test sent: {result}")


@router.post("/send", response_model=Message)
async def feishu_send_text(body: TextMessage) -> Any:
    """Send a custom text message to Feishu."""
    service = FeishuBotService()
    result = await service.send_text(body.message)
    return Message(message=f"Feishu message sent: {result}")


@router.post("/send-card", response_model=Message)
async def feishu_send_card(body: CardMessage) -> Any:
    """Send a card message to Feishu."""
    service = FeishuBotService()
    result = await service.send_card(body.title, body.content)
    return Message(message=f"Feishu card sent: {result}")
