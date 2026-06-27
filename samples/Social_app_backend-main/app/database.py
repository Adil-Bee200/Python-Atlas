from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


SQLALCHEMY_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind= engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:

#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='Kingofthenorth2004', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database succesfully connected")
#         break
#     except Exception as error:
#         print("Database not connected")
#         print("Error: ", error)
#         time.sleep(3)