"""
SQLAlchemy ORM model for Oracle DOCUMENTS table.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Sequence
)
from sqlalchemy.sql import func
from app.database import Base


# Oracle uses sequences + triggers for auto-increment
DOCUMENT_SEQ = Sequence("DOCUMENTS_SEQ", start=1, increment=1)


class Document(Base):
    __tablename__ = "DOCUMENTS"

    id = Column(
        Integer,
        DOCUMENT_SEQ,
        primary_key=True,
        server_default=DOCUMENT_SEQ.next_value(),
    )
    document_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)   # POLICY | REPORT | MEMO
    content = Column(Text, nullable=True)            # maps to CLOB in Oracle
    status = Column(String(20), nullable=False, default="DRAFT")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Document id={self.id} code={self.document_code!r}>"
