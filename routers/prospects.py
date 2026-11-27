from fastapi import APIRouter, Depends, Query, Request, UploadFile, status

from core.deps import DbSession, get_current_admin
from models.prospect import Prospect, ProspectDocument
from schemas.prospects import (
    ProspectCreate,
    ProspectDetailRead,
    ProspectDocumentRead,
    ProspectInteractionCreate,
    ProspectInteractionRead,
    ProspectRead,
    ProspectStatsRead,
    ProspectUpdate,
)
from services import prospects as prospects_service

router = APIRouter(
    prefix="/api/admin/prospects",
    tags=["Admin · Prospection commerciale"],
    dependencies=[Depends(get_current_admin)],
)


def _doc_to_read(doc: ProspectDocument, request: Request) -> ProspectDocumentRead:
    return ProspectDocumentRead(
        id=doc.id,
        prospect_id=doc.prospect_id,
        filename=doc.filename,
        original_name=doc.original_name,
        content_type=doc.content_type,
        size=doc.size,
        url=prospects_service.build_document_url(doc.filename, str(request.base_url)),
        created_at=doc.created_at,
    )


def _detail_to_read(prospect: Prospect, request: Request) -> ProspectDetailRead:
    base = ProspectRead.model_validate(prospect)
    return ProspectDetailRead(
        **base.model_dump(),
        interactions=[ProspectInteractionRead.model_validate(i) for i in prospect.interactions],
        documents=[_doc_to_read(d, request) for d in prospect.documents],
    )


@router.get("", response_model=list[ProspectRead])
def list_prospects(
    db: DbSession,
    search: str | None = None,
    status: str | None = None,
    sector: str | None = None,
    priority: str | None = None,
    archived: bool = False,
    sort: str = Query("updated_at", pattern="^(updated_at|created_at|next_follow_up_date)$"),
):
    return prospects_service.list_prospects(
        db,
        search=search,
        status=status,
        sector=sector,
        priority=priority,
        archived=archived,
        sort=sort,
    )


@router.get("/stats", response_model=ProspectStatsRead)
def prospect_stats(db: DbSession):
    return ProspectStatsRead(**prospects_service.get_stats(db))


@router.post("", response_model=ProspectDetailRead, status_code=status.HTTP_201_CREATED)
def create_prospect(payload: ProspectCreate, request: Request, db: DbSession):
    prospect = prospects_service.create_prospect(db, payload)
    return _detail_to_read(prospect, request)


@router.get("/{prospect_id}", response_model=ProspectDetailRead)
def get_prospect(prospect_id: int, request: Request, db: DbSession):
    prospect = prospects_service.get_prospect(db, prospect_id)
    return _detail_to_read(prospect, request)


@router.patch("/{prospect_id}", response_model=ProspectDetailRead)
def update_prospect(prospect_id: int, payload: ProspectUpdate, request: Request, db: DbSession):
    prospect = prospects_service.update_prospect(db, prospect_id, payload)
    return _detail_to_read(prospect, request)


@router.delete("/{prospect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prospect(prospect_id: int, db: DbSession):
    prospects_service.delete_prospect(db, prospect_id)


@router.post(
    "/{prospect_id}/interactions",
    response_model=ProspectInteractionRead,
    status_code=status.HTTP_201_CREATED,
)
def add_interaction(prospect_id: int, payload: ProspectInteractionCreate, db: DbSession):
    return prospects_service.add_interaction(db, prospect_id, payload)


@router.delete("/{prospect_id}/interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(prospect_id: int, interaction_id: int, db: DbSession):
    prospects_service.delete_interaction(db, prospect_id, interaction_id)


@router.post(
    "/{prospect_id}/documents",
    response_model=ProspectDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(prospect_id: int, file: UploadFile, request: Request, db: DbSession):
    doc = prospects_service.upload_document(db, prospect_id, file.file, file.filename or "", file.content_type)
    return _doc_to_read(doc, request)


@router.delete("/{prospect_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(prospect_id: int, doc_id: int, db: DbSession):
    prospects_service.delete_document(db, prospect_id, doc_id)
