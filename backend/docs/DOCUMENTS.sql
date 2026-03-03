-- =============================================================================
-- SQL DDL: Oracle DOCUMENTS table
-- Chapter 5: Oracle Database Integration
-- =============================================================================

-- 1. Drop existing objects (safe re-run)
BEGIN
    EXECUTE IMMEDIATE 'DROP TABLE DOCUMENTS CASCADE CONSTRAINTS';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

BEGIN
    EXECUTE IMMEDIATE 'DROP SEQUENCE DOCUMENTS_SEQ';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- 2. Sequence for auto-increment PK
CREATE SEQUENCE DOCUMENTS_SEQ
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;

-- 3. Main table
CREATE TABLE DOCUMENTS (
    id            NUMBER          CONSTRAINT pk_documents PRIMARY KEY,
    document_code VARCHAR2(50)    CONSTRAINT uq_documents_code UNIQUE NOT NULL,
    title         VARCHAR2(200)   NOT NULL,
    category      VARCHAR2(50)    NOT NULL
                  CONSTRAINT ck_documents_category
                  CHECK (category IN ('POLICY','REPORT','MEMO')),
    content       CLOB,
    status        VARCHAR2(20)    DEFAULT 'DRAFT' NOT NULL
                  CONSTRAINT ck_documents_status
                  CHECK (status IN ('DRAFT','ACTIVE','ARCHIVED','DELETED')),
    created_at    TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL,
    updated_at    TIMESTAMP       DEFAULT SYSTIMESTAMP NOT NULL
);

-- 4. Trigger: auto-set PK from sequence
CREATE OR REPLACE TRIGGER trg_documents_pk
    BEFORE INSERT ON DOCUMENTS
    FOR EACH ROW
BEGIN
    IF :NEW.id IS NULL THEN
        :NEW.id := DOCUMENTS_SEQ.NEXTVAL;
    END IF;
END;
/

-- 5. Trigger: auto-update updated_at on every UPDATE
CREATE OR REPLACE TRIGGER trg_documents_upd
    BEFORE UPDATE ON DOCUMENTS
    FOR EACH ROW
BEGIN
    :NEW.updated_at := SYSTIMESTAMP;
END;
/

-- 6. Indexes for common query patterns
CREATE INDEX idx_documents_category ON DOCUMENTS(category);
CREATE INDEX idx_documents_status   ON DOCUMENTS(status);
CREATE INDEX idx_documents_created  ON DOCUMENTS(created_at DESC);

-- 7. Seed data
INSERT INTO DOCUMENTS (document_code, title, category, content, status)
VALUES ('DOC-001', 'Kebijakan Keuangan 2025', 'POLICY',
        'Dokumen kebijakan keuangan perusahaan tahun 2025.', 'ACTIVE');

INSERT INTO DOCUMENTS (document_code, title, category, content, status)
VALUES ('DOC-002', 'Laporan Q1 2025', 'REPORT',
        'Laporan keuangan kuartal pertama tahun 2025.', 'ACTIVE');

INSERT INTO DOCUMENTS (document_code, title, category, content, status)
VALUES ('DOC-003', 'Memo Direksi Maret 2025', 'MEMO',
        'Memo internal dari direksi periode Maret 2025.', 'DRAFT');

COMMIT;

-- Verify
SELECT id, document_code, title, category, status FROM DOCUMENTS;
