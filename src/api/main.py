
import nonebot
from nonebot.log import logger
from fastapi import FastAPI

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
