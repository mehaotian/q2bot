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
    # 用户 ID
    user_id = fields.CharField(max_length=255, default="")
    # 群组 ID
    group_id = fields.CharField(max_length=255, default="")
    # 赢家 ID
    winner_id = fields.CharField(max_length=255, default="")
    # 当前持枪者
    current_user_id = fields.CharField(max_length=255, default="")
    # 玩家座位
    player_seat = fields.JSONField(default=[])
    # 参与人数
    player_count = fields.IntField(default=0)
    # 子弹数
    bullet_count = fields.IntField(default=6)
    # 子弹排列， 0 表示无，1表示有
    bullet_list = fields.JSONField(default=[])
    # 当前子弹位置 ，-1 表示无子弹,该装弹了
    current_bullet = fields.IntField(default=0)

    # 游戏状态 , 0 游戏未进行 1 游戏进行中 2 游戏结束
    status = fields.IntField(default=0)

    # 流程状态 0 装弹阶段 1 抽卡阶段（空弹进入） 2 前置buff判定阶段 3 用卡阶段 4 实时buff判定阶段 5 开枪阶段 6 后置buff判定 7 结算阶段（失败回到上一个阶段） 
    state = fields.IntField(0)
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
            record = await cls.get(id=game_id)
            record.status = 2
            await record.save()
            return record
        except DoesNotExist as e:
            logger.error(f"关闭游戏失败：{e}")
            return None

    @classmethod
    async def get_game(cls, gid: str, uid: str = None):
        """
        获取游戏
        参数：
            - gid: 群号
        返回：
            - CatGameTable
        """
        try:
            # 获取 gid ,并且 status 不是2 的所有数据
            print('uid', uid)
            if not uid:
                print(0)
                record = await cls.filter(group_id=gid).exclude(status=2)
            else:
                print(1)
                record = await cls.filter(group_id=gid, user_id=uid).exclude(status=2)

            print('record', record)
            if record and len(record) > 0:
                return record[0]
            return None
        except DoesNotExist:
            return None

   
