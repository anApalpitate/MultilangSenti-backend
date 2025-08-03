import os
from uuid import uuid4

import aiofiles
from fastapi import UploadFile
from sqlalchemy.orm import Session

from config import get_config
from model.userFile import UserFile
from util import log

UPLOAD_DIR = get_config().RESOURCE_PATH


# ---------------------------------------- 信息获取 ----------------------------------------
def get_by_category(db: Session, owner_id: int, category: str):
    return db.query(UserFile).filter(UserFile.owner_id == owner_id, UserFile.category == category).all()


# ---------------------------------------- 存储与删除 ----------------------------------------
def save_file_record(db: Session, filename: str, filepath: str, content_type: str, filesize: int, category: str,
                     owner_id: int):
    file = UserFile(
        filename=filename,
        filepath=filepath,
        content_type=content_type,
        filesize=filesize,
        category=category,
        owner_id=owner_id
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    return file


def delete_file_record(db: Session, file_id: int, user_id: int):
    file = db.query(UserFile).filter(UserFile.id == file_id, UserFile.owner_id == user_id).first()
    if file is None:
        return None
    db.delete(file)
    db.commit()
    return file


async def save_physical_file(file: UploadFile, category: str) -> str:
    """
    异步保存上传文件到指定目录，返回保存路径
    """
    if not file.filename:
        raise ValueError("文件名为空")
    ext = os.path.splitext(file.filename)[-1]
    unique_name = f"{uuid4().hex}{ext}"
    category_dir = os.path.join(UPLOAD_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    save_path = os.path.join(category_dir, unique_name)
    # 异步读取内容、写入文件
    contents = await file.read()
    async with aiofiles.open(save_path, "wb") as out_file:
        await out_file.write(contents)
    return save_path


def delete_physical_file(filepath: str):
    """
    从磁盘删除指定路径下的文件
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        log.info(f"删除路径:{filepath}的文件失败：{e}")
