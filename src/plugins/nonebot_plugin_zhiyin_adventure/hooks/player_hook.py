#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   player_flow.py
@Time    :   2024/06/21 16:09:14
@Author  :   haotian 
@Version :   1.0
@Desc    :   游戏玩家相关hook
'''
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
)

from ..models import ZyGameTable


class PlayerHook:
    bot: Bot = None
    event: GroupMessageEvent = None
    game = None
    group_id = ""
    user_id = ""
    game_id = ""

    def __init__(self, bot: Bot, event: GroupMessageEvent, game: ZyGameTable):
        """
        注册用户，初始化玩家数据
        参数：
          - bot: Bot
          - event: GroupMessageEvent
        """
        self.bot = bot
        self.event = event
        self.group_id = str(event.group_id)
        self.user_id = str(event.user_id)
        # 获取当前所在游戏数据
        self.game = game

    def set_coin(self, coin: int = 0):
        """
        设置只因币
        参数：
          - coin: 金币数量
        """
        print(self, coin)
