import os
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # tipos permitidos: imagem, áudio, vídeo, PDF
    allowed = ("image/", "audio/", "video/", "application/pdf")
    if not any(file.content_type.startswith(prefix) for prefix in allowed):
        raise HTTPException(400, "Tipo de arquivo não suportado")
    ext = os.path.splitext(file.filename)[1]
    file_id = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, file_id)
    with open(path, "wb") as out:
        shutil.copyfileobj(file.file, out)
    return JSONResponse({
        "url": f"/static/uploads/{file_id}",
        "filename": file.filename,
        "content_type": file.content_type
    })
