from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.database import connect_db, close_db, get_db
from .routers import auth, users, records, rankings, social_posts, teams

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await _ensure_indexes()
    yield
    await close_db()


async def _ensure_indexes() -> None:
    """启动时创建必要的 MongoDB 索引"""
    db = get_db()
    await db["users"].create_index("username", unique=True)
    await db["records"].create_index([("user_id", 1), ("date", 1)])
    await db["records"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["records"].create_index([("user_id", 1), ("habit_type", 1), ("date", 1)])
    await db["teams"].create_index("owner_user_id")
    await db["team_members"].create_index([("team_id", 1), ("user_id", 1)], unique=True)
    await db["team_members"].create_index("user_id", unique=True)
    await db["posts"].create_index([("created_at", -1)])
    await db["comments"].create_index([("post_id", 1), ("created_at", 1)])
    # 嵌套评论：按父评论 ID 查子回复
    await db["comments"].create_index([("parent_comment_id", 1), ("created_at", 1)])
    # 顶层热评查询：post_id + parent_comment_id 过滤
    await db["comments"].create_index([("post_id", 1), ("parent_comment_id", 1), ("created_at", 1)])
    await db["users"].create_index([("region.province_code", 1)], sparse=True)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="瘾了吗 —— 内部健康管理平台 API",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(records.router, prefix="/api/v1")
    app.include_router(rankings.router, prefix="/api/v1")
    app.include_router(social_posts.router, prefix="/api/v1")
    app.include_router(teams.router, prefix="/api/v1")

    @app.get("/", tags=["健康检查"])
    async def root():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
