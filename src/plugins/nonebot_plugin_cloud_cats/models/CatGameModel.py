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

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger


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
