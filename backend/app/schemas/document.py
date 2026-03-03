"""
Pydantic schemas for Document CRUD operations.
Provides strict validation AND the standard response envelope.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

# ── Shared constants ─────────────────────────────────────────────────────────
VALID_CATEGORIES = {"POLICY", "REPORT", "MEMO"}
VALID_STATUSES = {"DRAFT", "ACTIVE", "ARCHIVED", "DELETED"}


# ── Request schemas ───────────────────────────────────────────────────────────

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Annual Report 2025"])
    document_code: str = Field(..., min_length=1, max_length=50, examples=["DOC-001"])
    category: str = Field(..., examples=["POLICY"])
    content: Optional[str] = Field(None, examples=["Document body text…"])
    status: str = Field("DRAFT", examples=["DRAFT"])

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        upper = v.upper()
        if upper not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(VALID_CATEGORIES)}")
        return upper

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper = v.upper()
        if upper not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return upper


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    """All fields optional for partial-friendly full replacement."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    document_code: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        upper = v.upper()
        if upper not in VALID_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(VALID_CATEGORIES)}")
        return upper

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        upper = v.upper()
        if upper not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return upper


# ── Response schemas ──────────────────────────────────────────────────────────

class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Standard response envelope ────────────────────────────────────────────────

T = TypeVar("T")


class Meta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    meta: Optional[Meta] = None


class PaginatedDocuments(BaseModel):
    items: List[DocumentResponse]
