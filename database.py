from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# usa variables de entorno en render
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://us4teeml372nf9mpeihr:pAUq3DWX1iSJJn2BVZgEfqmCxEfVlL@bzfcugiuoiemcxv5dhfv-postgresql.services.clever-cloud.com:5432/bzfcugiuoiemcxv5dhfv"
)

engine = create_engine(
    DATABASE_URL,
    pool_size=2,        # máximo 2 conexiones vivas
    max_overflow=0,     # no crear conexiones extras (evita el error)
    pool_recycle=300,   # recicla conexiones cada 5 minutos
    pool_pre_ping=True  # prueba si está viva la conexión
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
