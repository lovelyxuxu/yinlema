from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.database import connect_db, close_db, get_db
from .routers import auth, users, records


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
    await db["records"].create_index([("user_id", 1), ("timestamp", -1)])
    await db["records"].create_index([("user_id", 1), ("date", 1)])


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="鹿了么 —— 男性健康自我管理工具后端 API",
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

    @app.get("/", tags=["健康检查"])
    async def root():
        return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

    return app


app = create_app()
