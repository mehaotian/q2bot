#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   game_hook.py
@Time    :   2024/04/22 18:52:39
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏主体钩子数据逻辑处理
'''

from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    GroupMessageEvent,
    MessageSegment,
)

from ..models.CatGameModel import CatGameTable

class GameHook:
    def __init__(self):
        pass

    @classmethod
    async def switch_game(cls, gid: str) -> Message:
        """
        开关游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        record = await CatGameTable.get_game(gid)

        if not record:
            # 创建游戏
            await CatGameTable.create(group_id=gid,status=1)
            record = await CatGameTable.get_game(gid)


        print(record)

        return Message(MessageSegment.text("游戏已开启"))
