from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://u4baiotbdceuaxwg2ncu:js8nStWdwjWyspHQXKlt@but30t5uca5pwxroeuxb-postgresql.services.clever-cloud.com:7121/but30t5uca5pwxroeuxb"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
