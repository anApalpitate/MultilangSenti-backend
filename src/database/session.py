import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import get_config
from util import log

db_path = get_config().DB_PATH


class _Database:
    def __init__(self, db_file_path: str):
        if not db_file_path.startswith("sqlite:///"):
            abs_path = os.path.abspath(db_file_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
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

    @contextmanager
    def db_session(self) -> Session:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


_db = _Database(db_path)
Base = _db.Base


def db_init():
    try:
        _db.init_db()
        log.info("⚙️ 数据库初始化完成")
    except Exception as e:
        log.error(f"❌ 数据库初始化失败: {e}")


def get_db():
    return next(_db.get_db())


def get_db_generator():
    return _db.get_db()


def db_session():
    return _db.db_session()
