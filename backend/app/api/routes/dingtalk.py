from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.models import Message
from app.services.dingtalk import DingTalkBotService

router = APIRouter(prefix="/dingtalk", tags=["dingtalk-webhook"])


class TextMessage(BaseModel):
    message: str


@router.post("/test", response_model=Message)
async def dingtalk_test() -> Any:
    """Send a test message to DingTalk."""
    service = DingTalkBotService()
    result = await service.send_text("Test message from API Automation Service.")
    return Message(message=f"DingTalk test sent: {result}")


@router.post("/send", response_model=Message)
async def dingtalk_send_text(body: TextMessage) -> Any:
    """Send a custom text message to DingTalk."""
    service = DingTalkBotService()
    result = await service.send_text(body.message)
    return Message(message=f"DingTalk message sent: {result}")
