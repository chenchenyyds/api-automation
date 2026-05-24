import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title="API Automation Service / API自动化服务",
    description="""
## API Automation Service | API自动化服务

A full-stack API automation platform with webhook integrations, health monitoring, and more.
全栈式API自动化平台，提供Webhook集成、健康监控等功能。

### Modules | 功能模块
* **Feishu / 飞书** - Send messages to Feishu via webhook / 通过Webhook发送飞书消息
* **DingTalk / 钉钉** - Send messages to DingTalk via webhook / 通过Webhook发送钉钉消息
* **Health / 健康检查** - System health monitoring / 系统健康监控
* **Users / 用户管理** - User management and authentication / 用户管理和认证
* **Items / 项目管理** - Sample CRUD items / 示例项目CRUD
""",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "filter": True,
    },
    version="1.0.0",
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
