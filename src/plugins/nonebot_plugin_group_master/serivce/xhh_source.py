#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   steam_source.py
@Time    :   2024/04/14 16:19:23
@Author  :   haotian
@Version :   1.0
@Desc    :   处理 小黑盒 相关数据
'''

from nonebot.adapters.onebot.v11 import (
    MessageSegment,
)
from nonebot.log import logger

from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned

from .user_source import create_user
from ..models.user_model import UserTable
from ..models.xhh_model import XhhTable

from ..config import plugin_config

async def bind_user(user_id: str, group_id: str, sender, xid: str) -> MessageSegment:

    # 检查用户，不存在则创建
    # 理论上讲，一个用户只应该存在一个 steam 账户
    await create_user(user_id, group_id, sender)
    user = await XhhTable.create_xhh_info(uid=user_id, xid=xid)
    return user

