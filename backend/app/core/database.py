from collections.abc import Generator
from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from app.core.config import settings

Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)

URL_BASE = f"sqlite:///{settings.database_path}"

engine = create_engine(
    URL_BASE,
    connect_args={"check_same_thread": False, "timeout": 15},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@event.listens_for(engine, "connect")
def _pragmas(conexion: Connection, _registro: ConnectionPoolEntry) -> None:
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
