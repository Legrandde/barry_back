import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from db.init_db import init_db
from routers import analytics, auth, collections, contact, media, prospects, public, sections
from services.exceptions import ServiceError

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_: FastAPI):
    if insecure := settings.insecure_defaults():
        message = f"Valeurs par défaut non sécurisées : {', '.join(insecure)}. Définissez-les dans le .env."
        if settings.is_production:
            raise RuntimeError(message)
        logger.warning(message)
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Mini CMS permettant à l'admin de modifier tout le contenu du portfolio d'Alhassane Barry sans redéploiement.",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
    return response


@app.exception_handler(ServiceError)
async def handle_service_error(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(auth.router)
app.include_router(public.router)
app.include_router(analytics.public_router)
app.include_router(contact.public_router)
app.include_router(sections.router)
for router in collections.routers:
    app.include_router(router)
app.include_router(media.router)
app.include_router(prospects.router)
app.include_router(analytics.admin_router)
app.include_router(contact.admin_router)

settings.media_dir.mkdir(parents=True, exist_ok=True)
app.mount(settings.media_url_path, StaticFiles(directory=settings.media_dir), name="media")


@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["Santé"])
def health() -> dict[str, str]:
    return {"status": "ok"}
