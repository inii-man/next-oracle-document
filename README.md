# Document Management System
## API & Git Engineering — Hari 3 (Chapter 5 & 6)

Aplikasi CRUD fullstack: **FastAPI + Oracle Database** (backend) dan **Next.js 15 App Router** (frontend).

---

## Struktur Proyek

```
oracle-next/
├── backend/
│   ├── app/
│   │   ├── main.py           ← FastAPI entry point
│   │   ├── database.py       ← Oracle connection pool (pool_size=20)
│   │   ├── models/
│   │   │   └── document.py   ← SQLAlchemy ORM
│   │   ├── schemas/
│   │   │   └── document.py   ← Pydantic schemas + response envelope
│   │   ├── routers/
│   │   │   └── documents.py  ← CRUD endpoints (5 endpoint)
│   │   └── deps/
│   │       └── auth.py       ← JWT auth dependency
│   ├── docs/
│   │   ├── DOCUMENTS.sql     ← Oracle DDL
│   │   └── postman_collection.json
│   ├── .env
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx
    │   ├── loading.tsx
    │   ├── error.tsx
    │   └── documents/
    │       ├── page.tsx      ← List + pagination + filter
    │       ├── new/page.tsx  ← Create form
    │       └── [id]/page.tsx ← Detail + edit + delete
    ├── components/
    │   ├── DocumentTable.tsx ← Responsive table + mobile cards
    │   ├── DocumentForm.tsx  ← React Hook Form + Zod
    │   └── Pagination.tsx
    ├── lib/
    │   └── api.ts            ← Typed fetch API helper
    └── .env.local
```

---

## Prasyarat

- Python 3.10+
- Node.js 18+
- Oracle Database XE / Free (sudah running di `localhost:1521`)
- Service name: `freepdb1`, user: `system`, password: `password`

---

## Langkah Setup

### 1. Setup Database Oracle

Jalankan DDL di Oracle SQL Developer atau sqlplus:

```sql
-- Jalankan file ini:
@backend/docs/DOCUMENTS.sql
```

### 2. Backend FastAPI

```bash
cd backend

# Buat virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Cek .env (sudah dikonfigurasi):
cat .env
# DATABASE_URL=oracle+oracledb://system:password@localhost:1521/freepdb1

# Jalankan server
uvicorn app.main:app --reload --port 8000
```

Backend akan berjalan di: **http://localhost:8000**
- Docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Frontend Next.js

```bash
cd frontend

# Install dependencies (sudah dilakukan, jalankan jika belum)
npm install

# Jalankan dev server
npm run dev
```

Frontend akan berjalan di: **http://localhost:3000**

---

## Endpoints API

| Method | Path | Deskripsi |
|--------|------|-----------|
| `GET` | `/health` | Health check + status DB |
| `GET` | `/v1/documents` | List + pagination + filter kategori |
| `GET` | `/v1/documents/{id}` | Detail dokumen |
| `POST` | `/v1/documents` | Create dokumen (201) |
| `PUT` | `/v1/documents/{id}` | Update dokumen |
| `DELETE` | `/v1/documents/{id}` | Soft delete (status=DELETED) |

### Query Parameters (GET /v1/documents)

| Param | Default | Contoh |
|-------|---------|--------|
| `page` | 1 | `?page=2` |
| `limit` | 20 | `?limit=10` |
| `category` | — | `?category=POLICY` |
| `search` | — | `?search=laporan` |

### Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "message": "Document created successfully",
  "meta": { "page": 1, "limit": 20, "total": 100, "total_pages": 5 }
}
```

---

## Test dengan Postman

Import file: `backend/docs/postman_collection.json`

Set variable `base_url` = `http://localhost:8000`

---

## Fitur Utama

- ✅ Connection pool Oracle (pool_size=20, pool_recycle=3600, pool_pre_ping)
- ✅ Parameter binding via SQLAlchemy ORM (no SQL injection)
- ✅ ACID transaction (commit on success, rollback on error)
- ✅ Soft delete (status='DELETED')
- ✅ Response envelope standar (`success`, `data`, `meta`)
- ✅ Pydantic validation + 422 error handling
- ✅ JWT auth (disabled by default, aktifkan via `REQUIRE_AUTH=true`)
- ✅ CORS configured untuk localhost:3000
- ✅ Loading spinner & error+retry di frontend
- ✅ Form validation (React Hook Form + Zod)
- ✅ Toast notifications (success/error)
- ✅ Delete confirmation dialog
- ✅ Responsive: table (desktop) + cards (mobile)
- ✅ Filter kategori + search
