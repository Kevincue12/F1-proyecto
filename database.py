from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://u4ziuizushhclxwvhjdr:wFYGaJtwlVSUIew6k8UcbzAscgjGiq@bnthfaq0mgettnlh3rrw-postgresql.services.clever-cloud.com:5432/bnthfaq0mgettnlh3rrw"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
