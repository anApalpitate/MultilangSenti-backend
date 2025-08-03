import os

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.auth import get_current_user
from database import get_db
from database.fileOperation import delete_file_record, delete_physical_file, save_file_record, save_physical_file
from model.user import User
from model.userFile import FileOut

file_router = APIRouter(prefix="/file", tags=["file"])


@file_router.post("/upload", response_model=FileOut)
async def upload_file(
        file: UploadFile = File(...),
        category: str = Form(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    try:
        save_path = await save_physical_file(file, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {e}")

    content_type = file.content_type or "application/octet-stream"
    try:
        file_record = save_file_record(
            db=db,
            filename=file.filename,
            filepath=save_path,
            content_type=content_type,
            filesize=os.path.getsize(save_path),
            category=category,
            owner_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件信息写入数据库失败: {e}")

    return file_record


@file_router.delete("/{file_id}")
def delete_file(
        file_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    file = delete_file_record(db, file_id, current_user.id)
    if file is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    delete_physical_file(file.filepath)
    return JSONResponse(content={"message": "删除成功"}, status_code=200)
