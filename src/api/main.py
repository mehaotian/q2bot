
import nonebot
from nonebot.log import logger
from fastapi import FastAPI

from .interface import (
    users
)


app: FastAPI = nonebot.get_app()

# 注册用户相关接口
app.include_router(users.router)

logger.success('多功能群管WEB面板加载成功')
