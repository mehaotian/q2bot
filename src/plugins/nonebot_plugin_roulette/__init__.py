from importlib import import_module
import_module('.models', __package__)

import re
from nonebot import (
    on_command
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    GroupMessageEvent,
)
from .utils import MsgText, At
from .hooks.game_hook import GameHook



start_game = on_command('来一盘刺激的轮盘赌', priority=1, block=True)

@start_game.handle()
async def start_game_handle(bot: Bot, event: GroupMessageEvent):
    uid = str(event.user_id)
    gid = str(event.group_id)
    msg = MsgText(event.json())
    params = msg.split(" ")

    # 如果第一个不存在或第一个参数不是 /来一盘刺激的轮盘赌 则返回错误
    if not params or params[0] != '/来一盘刺激的轮盘赌':
        return await bot.send(event, "指令错误, 示例：/来一盘刺激的轮盘赌")

    msg = await GameHook.create_game(group_id = gid)
    await bot.send(event, msg)