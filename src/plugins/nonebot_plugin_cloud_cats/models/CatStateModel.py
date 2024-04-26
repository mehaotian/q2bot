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
        'catdb.CatTable', related_name='cat', on_delete=fields.CASCADE)
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

    @classmethod
    async def update_state(cls, cat_id, **kwargs):
        """
        更新猫咪状态
        参数：
            - kwargs: 状态参数
        """
        record, _ = await CatStateTable.get_or_create(cat_id=cat_id)
        print(kwargs.items())
        for key, value in kwargs.items():
            setattr(record, key, value)
        return await record.save(update_fields=kwargs.keys())
