from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# This uses the DATABASE_URL from your config.py file
engine = create_engine(settings.DATABASE_URL)

# This is the SessionLocal your main.py needs to import
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)