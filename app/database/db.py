from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable is not set.")
    raise ValueError("database url is not set to the .env file!")

'''Engine with connection pooling for production'''
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=3600)

# Threads safe session
SessionLocal: sessionmaker[Session] = scoped_session(sessionmaker(bind=engine))

# Base class for ORM Models
Base: declarative_base = declarative_base()

''' Context manager for automatic session cleanup'''
from contextlib import contextmanager
@contextmanager
def get_db():
    try:
        session = SessionLocal()
        yield session
        session.commit()             # commit if everything goes well
    except:
        session.rollback()           # rollback en error
        raise
    finally:
        session.close()              # always close session


def test_db_connection():
    try:
        with engine.connect() as connection:
            print("MySQL database connected succesfully!")
        
    except Exception as e:
        print("MySQL connection Failed!!")
        print(f'Error: {str(e)}')
        raise e
    