#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   roulette_game.py
@Time    :   2024/04/28 16:59:37
@Author  :   haotian 
@Version :   1.0
@Desc    :   轮盘赌游戏模型
'''

import random
from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from nonebot.log import logger


class RouletteGameTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    #
    player = fields.ForeignKeyField(
        'default.RoulettePlayerTable', related_name='player', on_delete=fields.CASCADE)
    # 用户 ID
    # user_id = fields.CharField(max_length=255, default="")
    # 群组 ID
    group_id = fields.CharField(max_length=255, default="")
    # 赢家 ID
    winner_id = fields.CharField(max_length=255, default="")
    # 参与人数
    player_count = fields.IntField(default=0)
    # 子弹数
    bullet_count = fields.IntField(default=6)
    # 子弹排列， 0 表示无，1表示有
    bullet_list = fields.JSONField(default=[])
    # 当前子弹位置
    current_bullet = fields.IntField(default=0)

    # 游戏状态 , 0 游戏未进行 1 游戏进行中 2 游戏结束
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "roulette_game_table"
        table_description = "轮盘赌游戏战局表"

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
            record = await cls.create(group_id=gid, status=0)
            return record
        except Exception as e:
            logger.error(f"创建游戏失败：{e}")
            return None

    @classmethod
    async def close_game(cls, game_id: str):
        """
        关闭游戏
        参数：
            - game_id: 游戏id
        返回：
            - CatGameTable
        """
        try:
            record = await cls.get(game_id=game_id)
            record.status = 2
            await record.save()
            return record
        except DoesNotExist as e:
            logger.error(f"关闭游戏失败：{e}")
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
