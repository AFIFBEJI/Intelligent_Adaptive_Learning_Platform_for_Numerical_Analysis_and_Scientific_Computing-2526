from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

# URL read from .env - the password is no longer visible in the code!
settings = get_settings()

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Open a connection and close it automatically after each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create the tables in PostgreSQL at startup if they do not exist."""
    Base.metadata.create_all(bind=engine)

