import pathlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routers.chat import router as chat_router
from app.routers.room import router as rooms_router
from app.routers.upload import router as upload_router

app = FastAPI()

# Endpoints de salas e chat
app.include_router(rooms_router, prefix="/rooms", tags=["rooms"])
app.include_router(chat_router, prefix="/ws", tags=["chat"])

# Upload de arquivos
app.include_router(upload_router, prefix="/files", tags=["files"])
app.mount(
    "/static/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# Página principal
@app.get("/", response_class=HTMLResponse)
async def get_index():
    html = pathlib.Path("index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
