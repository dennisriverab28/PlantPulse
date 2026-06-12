from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import settings


class Base(DeclarativeBase):
    pass


def _engine_kwargs() -> dict:
    kwargs: dict = {"pool_pre_ping": True}
    if settings.database_url.startswith("sqlite"):
        # FastAPI serves sync endpoints from a threadpool.
        kwargs["connect_args"] = {"check_same_thread": False}
        if settings.database_url in ("sqlite://", "sqlite:///:memory:"):
            # In-memory DBs vanish per-connection; pin everything to one.
            kwargs["poolclass"] = StaticPool
    return kwargs


engine = create_engine(settings.database_url, **_engine_kwargs())
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
