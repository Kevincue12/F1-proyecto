from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://ult5rgyuvz3qyxa9rdlz:Pngm997JxisgW6l7vBn9@baqvwdbcl0daxl9pcowv-postgresql.services.clever-cloud.com:7783/baqvwdbcl0daxl9pcowv"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
