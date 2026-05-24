import sys
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from sqlmodel import text

from app.api.deps import SessionDep
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/detailed")
async def health_check_detailed(session: SessionDep) -> dict[str, Any]:
    """Detailed health check with DB, Redis, and Celery status."""
    db_status = "ok"
    try:
        session.exec(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    redis_status = "unknown"
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, socket_connect_timeout=2)
        if r.ping():
            redis_status = "ok"
        else:
            redis_status = "error: no ping response"
    except ImportError:
        redis_status = "not_installed"
    except Exception as e:
        redis_status = f"error: {str(e)}"

    celery_status = "unknown"
    try:
        from app.core.celery_app import celery_app
        insp = celery_app.control.inspect()
        stats = insp.stats()
        if stats:
            celery_status = "ok"
        else:
            celery_status = "no_workers"
    except ImportError:
        celery_status = "not_installed"
    except Exception as e:
        celery_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.PROJECT_NAME,
        "python_version": sys.version,
        "database": db_status,
        "redis": redis_status,
        "celery": celery_status,
    }
