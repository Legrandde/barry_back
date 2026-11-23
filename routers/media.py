from fastapi import APIRouter, BackgroundTasks, Depends, Request, UploadFile, status

from core.deps import DbSession, get_current_admin
from models import Media
from schemas.media import MediaRead
from services import media as media_service

router = APIRouter(
    prefix="/api/admin/media",
    tags=["Admin · Médias"],
    dependencies=[Depends(get_current_admin)],
)


def _to_read(media: Media, request: Request) -> MediaRead:
    return MediaRead(
        id=media.id,
        filename=media.filename,
        original_name=media.original_name,
        content_type=media.content_type,
        size=media.size,
        status=media.status,
        original_size=media.original_size,
        url=media_service.build_url(media.filename, str(request.base_url)),
        created_at=media.created_at,
    )


@router.get("", response_model=list[MediaRead])
def list_media(request: Request, db: DbSession):
    return [_to_read(media, request) for media in media_service.list_media(db)]


@router.post("", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
def upload_media(file: UploadFile, request: Request, db: DbSession, background_tasks: BackgroundTasks):
    """Téléverse une image ou une vidéo. L'URL retournée s'utilise dans les champs image du contenu.

    Une vidéo lourde est compressée en arrière-plan (statut "processing") ; elle reste utilisable
    pendant ce temps et garde la même URL.
    """
    media = media_service.save_upload(db, file.file, file.filename or "", file.content_type)
    if media.status == "processing":
        background_tasks.add_task(media_service.compress_media, media.id)
    return _to_read(media, request)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(media_id: int, db: DbSession):
    media_service.delete_media(db, media_id)
