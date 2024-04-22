#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   CatStateModel.py
@Time    :   2024/04/22 11:53:06
@Author  :   haotian 
@Version :   1.0
@Desc    :   猫咪状态模型
'''


from tortoise.models import Model
from tortoise import fields

class CatStateTable(Model):
    id = fields.IntField(pk=True)
    # 外键关联猫咪
    cat = fields.ForeignKeyField(
        'catdb.CatTable', related_name='state', on_delete=fields.CASCADE)
    # 饱食度
    hunger = fields.IntField(default=100)
    # 清洁度
    cleanless = fields.IntField(default=100)
    # 快乐度
    happiness = fields.IntField(default=100)
    # 疲劳度
    fatigue = fields.IntField(default=100)
    # 睡眠
    sleep = fields.IntField(default=100)
    # 健康
    health = fields.IntField(default=100)

    # 最后更新时间
    last_update = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "cat_state_table"  # 数据库中的表名
        table_description = "猫咪状态表"