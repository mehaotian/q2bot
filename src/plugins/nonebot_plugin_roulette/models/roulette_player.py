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
    # 用户 ID,外键关联用户
    user = fields.ForeignKeyField(
        'userdb.UserTable', related_name='roulette_player', on_delete=fields.CASCADE)
    # 游戏 ID
    game_id = fields.CharField(max_length=255, default="")
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
    card_slot = fields.JSONField(default=[0, 0, 0, 0])

    # 玩家状态 0 参与中 1 胜利 2 失败
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "roulette_player_table"
        table_description = "轮盘赌游戏玩家表"
