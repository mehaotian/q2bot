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
from nonebot.rule import to_me

from ..hooks.game_hook import GameHook

gameReg = r"^\s*(开启|关闭)只因大冒险\s*$"
game = on_regex(gameReg, rule=to_me(), priority=20, block=True)


join_game = on_fullmatch("加入只因世界", rule=to_me(), priority=20, block=True)


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


@join_game.handle()
async def join_game_handle(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    uid = str(event.user_id)
    msg = await GameHook.join_game(gid=gid,uid=uid)

    await bot.send(event=event, message=msg)