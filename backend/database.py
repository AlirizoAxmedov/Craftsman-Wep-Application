from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Create engine with connection pooling configuration
# SQLite doesn't use pool_size, so we check the database type
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support connection pooling parameters
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,  # Set to True for debugging
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Test connections before using
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency for database session in FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()