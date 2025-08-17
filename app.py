from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "webapp")

# Отдаём статические файлы, если появятся (картинки/стили)
app.mount("/static", StaticFiles(directory=os.path.join(WEB_DIR, "static")), name="static")

@app.get("/app", response_class=HTMLResponse)
async def webapp(_: Request):
    index_path = os.path.join(WEB_DIR, "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse("<h1>WebApp not found</h1><p>Create webapp/index.html</p>", status_code=500)
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
