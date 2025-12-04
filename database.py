from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://urkeuyjxokgw5cshigb4:oua9RsoQ7Vx9t0g760DiXJxjP8ShMY@bn80ksk4mopvfgmrudir-postgresql.services.clever-cloud.com:5432/bn80ksk4mopvfgmrudir"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
