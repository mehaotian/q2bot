import nonebot
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message
)
from fastapi import FastAPI
from nonebot.log import logger

app: FastAPI = nonebot.get_app()

logger.info('API 接口：加载成功')

@app.get("/")
async def custom_api():
    bot:Bot = get_bot()
    print(bot)
    res =  await bot.send_group_msg(group_id=695239108, message=Message('Hello, world!'))
    print(res)

    return {"message": "Hello, world!"}