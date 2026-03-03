"""
CRUD router for /v1/documents
All endpoints use parameter binding via SQLAlchemy ORM (no raw SQL → no SQL injection).
Transactions are ACID: commit on success, rollback on error.
"""
from __future__ import annotations

import math
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.deps.auth import get_current_user
from app.models.document import Document
from app.schemas.document import (
    ApiResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    Meta,
    PaginatedDocuments,
)

router = APIRouter(prefix="/v1/documents", tags=["documents"])


# ── Helper ────────────────────────────────────────────────────────────────────

def _get_or_404(db: Session, doc_id: int) -> Document:
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.status != "DELETED",
    ).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id={doc_id} not found",
        )
    return doc


# ── GET /v1/documents ─────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=ApiResponse[PaginatedDocuments],
    summary="List documents with pagination & category filter",
)
def list_documents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title / document_code"),
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    query = db.query(Document).filter(Document.status != "DELETED")

    if category:
        query = query.filter(Document.category == category.upper())

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Document.title.ilike(pattern) | Document.document_code.ilike(pattern)
        )

    total = query.count()
    total_pages = math.ceil(total / limit) if total else 1
    offset = (page - 1) * limit
    items = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()

    return ApiResponse(
        success=True,
        data=PaginatedDocuments(items=items),
        meta=Meta(page=page, limit=limit, total=total, total_pages=total_pages),
    )


# ── GET /v1/documents/{id} ────────────────────────────────────────────────────

@router.get(
    "/{doc_id}",
    response_model=ApiResponse[DocumentResponse],
    summary="Get document by ID",
)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    doc = _get_or_404(db, doc_id)
    return ApiResponse(success=True, data=DocumentResponse.model_validate(doc))


# ── POST /v1/documents ────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
)
def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    doc = Document(**payload.model_dump())
    db.add(doc)
    try:
        db.commit()
        db.refresh(doc)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"document_code '{payload.document_code}' already exists",
        )
    return ApiResponse(
        success=True,
        data=DocumentResponse.model_validate(doc),
        message="Document created successfully",
    )


# ── PUT /v1/documents/{id} ────────────────────────────────────────────────────

@router.put(
    "/{doc_id}",
    response_model=ApiResponse[DocumentResponse],
    summary="Full update (all fields) of a document",
)
def update_document(
    doc_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    doc = _get_or_404(db, doc_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doc, field, value)

    try:
        db.commit()
        db.refresh(doc)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"document_code '{payload.document_code}' already exists",
        )
    return ApiResponse(
        success=True,
        data=DocumentResponse.model_validate(doc),
        message="Document updated successfully",
    )


# ── DELETE /v1/documents/{id} ─────────────────────────────────────────────────

@router.delete(
    "/{doc_id}",
    response_model=ApiResponse[DocumentResponse],
    summary="Soft-delete document (sets status='DELETED')",
)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    doc = _get_or_404(db, doc_id)
    doc.status = "DELETED"
    db.commit()
    db.refresh(doc)
    return ApiResponse(
        success=True,
        data=DocumentResponse.model_validate(doc),
        message="Document deleted successfully",
    )
