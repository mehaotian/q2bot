#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   CatGameModels.py
@Time    :   2024/04/17 21:38:25
@Author  :   haotian 
@Version :   1.0
@Desc    :   猫咪行为模型
'''

from tortoise import fields
from tortoise.models import Model

from nonebot.log import logger


class ActionsTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 外键关联猫咪
    cat = fields.ForeignKeyField(
        'catdb.CatTable', related_name='actions', on_delete=fields.CASCADE)
    # 行为名称
    action_name = fields.CharField(max_length=255, default="")
    # 饱食度影响
    hunger_effect = fields.IntField(default=0)
    # 清洁度影响
    cleanless_effect = fields.IntField(default=0)
    # 快乐度影响
    happiness_effect = fields.IntField(default=0)
    # 疲劳度影响
    fatigue_effect = fields.IntField(default=0)
    # 睡眠影响
    sleep_effect = fields.IntField(default=0)
    # 健康影响
    health_effect = fields.IntField(default=0)

    # 行为类别 0 猫咪行为 1 道具行为 2 事件行为 3 游戏行为 
    action_type = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "actions_table"
        table_description = "行为表"
