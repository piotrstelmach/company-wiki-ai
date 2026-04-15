import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

# Load environment variables from the .env file in the root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

def create_db_and_tables() :
    SQLModel.metadata.create_all(engine)

def db_connection():
    with Session(engine) as session:
        yield session
