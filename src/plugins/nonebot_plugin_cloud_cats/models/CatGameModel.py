#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   CatGameModels.py
@Time    :   2024/04/17 21:38:25
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏记录模型
'''

# from pydantic import BaseModel

import random
from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from nonebot.log import logger
from nonebot_plugin_tortoise_orm import add_model
from ..config import global_config

# 添加模型
# db_url = global_config.cat_db_url
# add_model(model=__name__, db_name='catdb', db_url=db_url)

class CatGameTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 用户 ID ，使用str ，int容易超过范围
    user_id = fields.CharField(max_length=255, default="")
    # 群组 ID ，使用str ，int容易超过范围
    group_id = fields.CharField(max_length=255, default="")
    # 游戏状态 , 0 游戏未进行 1 游戏进行中
    status = fields.IntField(default=0)
    
    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "cat_game_table"
        table_description = "游戏表"

    @classmethod
    async def create_game(cls, gid: str):
        """
        创建默认游戏游戏
        参数：
            - gid: 群号
        返回：
            - CatGameTable
        """
        try:
            record = await cls.create(group_id=gid,status=0)
            return record
        except Exception as e:
            logger.error(f"创建游戏失败：{e}")
            return None

    @classmethod
    async def get_game(cls, gid: str):
        """
        获取游戏
        参数：
            - gid: 群号
        返回：
            - CatGameTable
        """
        try:
            record = await cls.get(group_id=gid)
            return record            
        except DoesNotExist:
            return None
