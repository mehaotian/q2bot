#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   roulette_game.py
@Time    :   2024/04/28 16:59:37
@Author  :   haotian 
@Version :   1.0
@Desc    :   轮盘赌道具模型
'''

import random
from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from nonebot.log import logger


class RouletteCardTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 卡片效果类型
    type = fields.IntField(default=0)

    # 游戏状态 , 0 游戏未进行 1 游戏进行中 2 游戏结束
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "roulette_card_table"
        table_description = "轮盘赌道具表"
   