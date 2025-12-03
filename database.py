from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://ufmywtllyvkjossfaovu:PSy0HtVX9VtK1o5YziAXgVTfLwDQZq@bqq0odfjllt6x7fmua8l-postgresql.services.clever-cloud.com:5432/bqq0odfjllt6x7fmua8l"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
