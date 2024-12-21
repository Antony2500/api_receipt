import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.api.routers.users import router as user_router
from app.api.routers.auth import router as auth_router
from app.config import settings, config
from app.database import sessionmanager

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.log_level == "DEBUG" else logging.INFO)

root_logger = logging.getLogger("root_logger")


def get_application(settings_db: str = "", init_db: bool = True) -> FastAPI:
    if init_db:
        sessionmanager.init(settings_db)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")
    app.add_middleware(SessionMiddleware, secret_key="some-random-string")

    @app.middleware("http")
    async def exception_handling(request: Request, call_next):
        root_logger.info(
            f"Url: {request.url}\n"
            f"Header: {request.headers}\n"
            f"Method: {request.method}\n"
            f"Query params: {request.query_params}\n"
            f"Path params: {request.path_params}\n"
        )
        try:
            return await call_next(request)
        except Exception as exc:
            root_logger.error(str(exc), exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)},
            )

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    app.include_router(user_router)
    app.include_router(auth_router)

    return app


app = get_application(settings.database_config.DB_CONFIG[0])


def init_app(init_db=True):
    lifespan = None

    if init_db:
        sessionmanager.init(config.DB_CONFIG)

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()

    server = FastAPI(title="FastAPI server", lifespan=lifespan)
    server.add_middleware(SessionMiddleware, secret_key="some-random-string")

    @server.get("/")
    async def root():
        return {"message": "Hello World"}

    server.include_router(user_router)
    server.include_router(auth_router)

    return app
