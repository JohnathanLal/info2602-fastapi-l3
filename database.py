from sqlmodel import SQLModel, Session, create_engine
from contextlib import contextmanager

DATABASE_URL = "sqlite:///./todo_app.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_all():
    SQLModel.metadata.drop_all(engine)

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session