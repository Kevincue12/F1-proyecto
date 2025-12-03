from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://unpegsjwael9cdtu9vbs:8SajK4T14Hu5qj9YaAXJqrkPPetfKJ@bcsmtqh7mlaclbeacsm9-postgresql.services.clever-cloud.com:5432/bcsmtqh7mlaclbeacsm9"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
