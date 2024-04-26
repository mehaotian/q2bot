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
            return record
        return None
    async def check_cat(gid):
        """
        检查猫咪是否存在
        参数：
            - gid: 群号
        返回：
            - bool
        """
        record = await CatGameTable.get_game(gid)
        if not record:
            return Message(MessageSegment.text("云养猫游戏未开启"))
        cat_record = await CatTable.get_cat(record.id)
        if cat_record:
            return cat_record
        return Message(MessageSegment.text("猫咪不存在"))
    
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
        
        cat_record = await CatTable.get_cat(record.id)
        if cat_record:
            return Message(MessageSegment.text("猫咪已经存在"))
        # 创建猫咪
        if record := await CatTable.create_cat(record.id,gid):
            return Message(MessageSegment.text("猫咪创建成功"))
        
        return Message(MessageSegment.text("猫咪创建失败"))
    
    async def get_cat_info(gid:str)->Message:
        """
        获取猫咪信息
        参数：
            - gid: 群号
        返回：
            - Message
        """
        record = await CatGameTable.get_game(gid)
        if not record:
            return Message(MessageSegment.text("云养猫游戏未开启"))
        
        cat_info = await CatTable.get_cat(record.id)

        if not cat_info:
            return Message(MessageSegment.text("猫咪不存在"))

        return Message(MessageSegment.text(f"猫咪名称：{cat_info['name']}\n年龄：{cat_info['age']}\n体重：{cat_info['weight']}\n形象：{cat_info['image']}\n性格：{cat_info['character']}\n品种：{cat_info['breed']}\n性别：{cat_info['sex']}"))

    
    @classmethod
    async def update_cat(cls,gid:str)->Message:
        """
        更新猫咪信息
        参数：
            - gid: 群号
        返回：
            - Message
        """

        check_cat = await cls.check_cat(gid)
        if not check_cat:
            return check_cat
        

        
        
        return Message(MessageSegment.text("猫咪信息更新失败"))
