from datetime import datetime
from datetime import timezone

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.session import Base


class UserFile(Base):
    __tablename__ = "user_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)  # 后端保存路径
    content_type = Column(String(50), nullable=False)  # 文件类型
    filesize = Column(Integer, nullable=False)

    category = Column(String, nullable=False)  # 文件分类
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="files")
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FileBase(BaseModel):
    filename: str
    content_type: str
    filesize: int


class FileCreate(FileBase):
    pass


class FileOut(FileBase):
    id: int
    filepath: str
    upload_time: datetime
    owner_id: int
    category: str

    class Config:
        from_attributes = True
