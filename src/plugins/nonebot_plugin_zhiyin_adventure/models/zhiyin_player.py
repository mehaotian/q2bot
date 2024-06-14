#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   zhiyin_player.py
@Time    :   2024/06/14 13:20:47
@Author  :   haotian 
@Version :   1.0
@Desc    :   只因大冒险玩家模型
'''

from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import DoesNotExist

from nonebot.log import logger


class ZyPlayerTable(Model):
    # 自增 ID (Primary key)
    id = fields.IntField(pk=True, generated=True)
    # 游戏 ID
    game = fields.ForeignKeyField(
        'zhiyindb.ZyGameTable', related_name='game')
    # 用户 ID,外键关联用户
    user_id = fields.CharField(max_length=255, default="")
    # 群组 ID
    group_id = fields.CharField(max_length=255, default="")

    # 玩家状态 0 未加入 1 游戏中 
    status = fields.IntField(default=0)

    # 创建时间
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "zhiyin_player_table"
        table_description = "只因大冒险玩家表"
    