"""
Oracle Database connection pool using SQLAlchemy + python-oracledb
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
import oracledb
from dotenv import load_dotenv
import os

load_dotenv()

# Use python-oracledb in thin mode (no Oracle Instant Client needed)
oracledb.init_oracle_client()  # comment this out if using thin mode

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "oracle+oracledb://user:pass@localhost:1521/XEPDB1"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # max persistent connections
    max_overflow=0,        # no extra connections beyond pool_size
    pool_pre_ping=True,    # verify connection before use
    pool_recycle=3600,     # recycle connections every 1 hour
    echo=False,            # set True to log SQL (debug only)
    poolclass=QueuePool,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yield a DB session, always close on exit."""
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """Health-check: verify Oracle connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1 FROM DUAL"))
        return True
    except Exception:
        return False
