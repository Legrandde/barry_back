import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import settings
from db.init_db import init_db
from routers import analytics, auth, collections, contact, media, public, sections
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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
app.include_router(analytics.admin_router)
app.include_router(contact.admin_router)

settings.media_dir.mkdir(parents=True, exist_ok=True)
app.mount(settings.media_url_path, StaticFiles(directory=settings.media_dir), name="media")


@app.get("/api/health", tags=["Santé"])
def health() -> dict[str, str]:
    return {"status": "ok"}
