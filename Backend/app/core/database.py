from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
engine = create_engine(settings.DATABASE_URL)

session_locale = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    session=session_locale()
    try:
        yield session
    finally:
        session.close()
        