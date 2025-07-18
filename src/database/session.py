import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class _Database:
    def __init__(self, db_file_path: str):
        if not db_file_path.startswith("sqlite:///"):
            abs_path = os.path.abspath(db_file_path)
            database_url = f"sqlite:///{abs_path}"
        else:
            database_url = db_file_path

        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self.Base = declarative_base()

    def init_db(self):
        self.Base.metadata.create_all(bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


_db = _Database("../resources/data.db")
Base = _db.Base


def db_init():
    _db.init_db()


def get_db():
    return _db.get_db()
