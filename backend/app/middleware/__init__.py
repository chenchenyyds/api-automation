import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

# In-memory rate limit tracker. Replace with Redis for production.
_rate_window: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request, key_id: str, limit: int = 100) -> None:
    """Raise HTTPException(429) if the key has exceeded its per-minute limit."""
    now = time.time()
    window_start = now - 60
    _rate_window[key_id] = [t for t in _rate_window[key_id] if t > window_start]

    if len(_rate_window[key_id]) >= limit:
        retry_after = int(60 - (now - _rate_window[key_id][0]))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after}s",
            headers={"Retry-After": str(retry_after)},
        )

    _rate_window[key_id].append(now)
