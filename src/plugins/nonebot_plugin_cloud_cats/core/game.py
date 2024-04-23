#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   game.py
@Time    :   2024/04/18 00:33:47
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏主体
'''
from nonebot import (
    on_fullmatch,
    on_regex
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    MessageSegment,
)

from ..hooks.game_hook import GameHook

gameReg = r"^\s*(开启|关闭)云养猫\s*$"
game = on_regex(gameReg, priority=20, block=True)
create_game = on_fullmatch("创建猫咪", priority=20, block=True)


@game.handle()
async def game_handle(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    msgdata = event.get_message()
    msgdata = msgdata.extract_plain_text().strip()

    # 如果包含 开启
    if "开启" in msgdata:
        msgdata = 1
    else:
        msgdata = 0
    print(msgdata)
    msg = await GameHook.switch_game(gid, msgdata)

    await bot.send(event=event, message=msg)

@create_game.handle()
async def create_game_handle(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    msg = await GameHook.create_cat(gid)
    await bot.send(event=event, message=msg)