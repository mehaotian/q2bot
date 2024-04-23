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
from ..models.CatModel import CatTable

class GameHook:
    def __init__(self):
        pass

    @classmethod
    async def switch_game(cls, gid: str,type:int) -> Message:
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

        if record.status == type:
            msg = "云养猫游戏已经开启了,请勿重复操作" if type == 1 else "云养猫游戏已经关闭了，请勿重复操作"
            return Message(MessageSegment.text(msg))

        record.status = type
        await record.save(update_fields=['status'])
        if type == 0:
            msg = "云养猫游戏已关闭"
        else:
            msg = "云养猫游戏已开启"

        return Message(MessageSegment.text(msg))
    
    async def check_game (gid:str)->bool:
        """
        检查游戏是否开启
        参数：
            - gid: 群号
        返回：
            - bool
        """
        record = await CatGameTable.get_game(gid)
        if record.status == 1:
            return True
        return False
    
    async def create_cat(gid:str)->Message:
        """
        创建猫咪
        参数：
            - gid: 群号
        返回：
            - Message
        """
        record = await CatGameTable.get_game(gid)
        if not record:
            return Message(MessageSegment.text("云养猫游戏未开启"))
        # 创建猫咪
        if record := await CatTable.create_cat(record.id,gid):
            return Message(MessageSegment.text("猫咪创建成功"))
        
        return Message(MessageSegment.text("猫咪创建失败"))
    
