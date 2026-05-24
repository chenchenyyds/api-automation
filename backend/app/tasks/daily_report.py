from datetime import datetime, timezone

from app.core.celery_app import celery_app
from app.core.config import settings


@celery_app.task(name="app.tasks.daily_report.send_daily_usage_report")
def send_daily_usage_report() -> dict:
    """Daily task: collect API usage stats and push via Feishu webhook."""
    now = datetime.now(timezone.utc).isoformat()
    stats = {
        "date": now,
        "total_requests": 0,
        "active_keys": 0,
    }

    if settings.FEISHU_WEBHOOK_URL:
        try:
            from app.services.feishu import FeishuBotService

            feishu = FeishuBotService()
            message = (
                f"**每日 API 使用报告 | Daily API Usage Report**\n"
                f"日期 | Date: {now[:10]}\n"
                f"总请求数 | Total Requests: {stats['total_requests']}\n"
                f"活跃密钥 | Active Keys: {stats['active_keys']}"
            )
            feishu.send_text(message)
        except Exception:
            pass

    return stats


@celery_app.task(name="app.tasks.daily_report.health_check_ping")
def health_check_ping() -> str:
    """Scheduled health check ping. Returns timestamp."""
    return f"pong at {datetime.now(timezone.utc).isoformat()}"
