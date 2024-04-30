#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   roulette_game.py
@Time    :   2024/04/28 16:59:37
@Author  :   haotian 
@Version :   1.0
@Desc    :   轮盘赌游戏玩家模型
'''

import random
from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from nonebot.log import logger


class RoulettePlayerTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 游戏 ID
    game = fields.ForeignKeyField(
        'roulettedb.RouletteGameTable', related_name='game')
    # 用户 ID,外键关联用户
    user_id = fields.CharField(max_length=255, default="")
    # game_id = fields.CharField(max_length=255, default="")
    # 群组 ID
    group_id = fields.CharField(max_length=255, default="")
    # 命数
    life = fields.IntField(default=3)

    # 空弹统计，自己打自己空弹
    empty_count = fields.IntField(default=0)
    # 空弹统计，打别人空弹
    other_empty_count = fields.IntField(default=0)
    # 空弹统计，他人打自己空弹
    be_empty_count = fields.IntField(default=0)

    # 击中次数 ，自己击中自己
    hit_count = fields.IntField(default=0)
    # 击中次数 ，自己击中他人
    other_hit_count = fields.IntField(default=0)
    # 击中次数 ，他人击中自己
    be_hit_count = fields.IntField(default=0)

    # 开枪次数
    shoot_count = fields.IntField(default=0)
    # 向自己开枪次数
    shoot_self_count = fields.IntField(default=0)
    # 想别人开枪次数
    shoot_other_count = fields.IntField(default=0)

    # 使用卡片次数
    use_card_count = fields.IntField(default=0)

    # 跳过次数
    skip_count = fields.IntField(default=0)

    # 筹码
    chips = fields.IntField(default=50)

    # 卡片槽位 4 个 [0,0,0,0]
    card_slot = fields.JSONField(default=[])

    # 后置buff
    buff = fields.JSONField(default=[])
    # 前置debuff
    debuff = fields.JSONField(default=[])

    # 伤害倍率
    damage_rate = fields.IntField(default=1)

    # 玩家状态 0 参与中 1 胜利 2 失败
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "roulette_player_table"
        table_description = "轮盘赌游戏玩家表"

    @classmethod
    async def create_player(cls, gid: str, uid: str, game_id: str):
        """
        创建玩家
        参数：
            - gid: 群号
            - uid: 用户 ID
            - game_id: 游戏 ID
        返回：
            - RoulettePlayerTable
        """
        try:
            record = await cls.create(group_id=gid, user_id=uid, game_id=game_id)
            return record
        except Exception as e:
            logger.error(f"创建玩家失败：{e}")
            return None
    @classmethod
    async def get_player(cls, game_id: str, uid: str):
        """
        获取玩家
        参数：
            - game_id: 游戏id
            - uid: 用户id
        返回：
            - RoulettePlayerTable
        """
        try:
            record = await cls.get(game_id=game_id,user_id=uid)
            return record
        except DoesNotExist:
            return None
    @classmethod
    async def get_game_players(cls, game_id: str):
        """
        获取玩家
        参数：
            - game_id: 游戏id
        返回：
            - RoulettePlayerTable
        """
        try:
            record = await cls.filter(game_id=game_id).all()
            return record
        except DoesNotExist:
            return None