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
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    MessageSegment,
)
print("game.py")
game = on_fullmatch("开启", priority=1, block=False)

@game.handle()
async def game_handle(bot: Bot, event: GroupMessageEvent):
    print('----',event.get_session_id())
    await game.send("游戏功能暂未开放，敬请期待！")