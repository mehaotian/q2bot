import os
import nonebot
from nonebot.log import logger
from fastapi import FastAPI,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .interface import (
    users,
    system
)


app: FastAPI = nonebot.get_app()

# 注册用户相关接口
app.include_router(users.router)

# 系统相关
app.include_router(system.router)

logger.success('多功能群管WEB面板加载成功')



BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name="dist")
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, 'static/assets')), name="assets")

@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    if path.startswith("api"):
        raise HTTPException(status_code=404)
    return main()

@app.get("/")
def main():
    html_path = os.path.join(BASE_DIR, 'static', 'index.html')
    html_content = ''
    with open(html_path) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)