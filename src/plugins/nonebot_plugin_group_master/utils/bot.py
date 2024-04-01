#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   bot.py
@Time    :   2024/04/01 17:08:00
@Author  :   haotian 
@Version :   1.0
@Desc    :   Bot 相关接口调用
'''

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot

class GetBot:
    def __init__(self) -> None:
        """
        > 获取 Bot 实例
        """
        self.bot:Bot = get_bot()

    async def get_group_member_info(self, group_id:int, user_id:int):
        """
        > 获取群成员信息
        参数：
        - `group_id:int`: 群ID
        - `user_id:int`: 用户ID

        返回：
        - `dict`: 群成员信息
        """
        return await self.bot.get_group_member_info(group_id=group_id, user_id=user_id)
    

user_bot = GetBot()