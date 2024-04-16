#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   lottery_source.py
@Time    :   2024/04/16 10:40:49
@Author  :   haotian 
@Version :   1.0
@Desc    :   抽奖操作
'''


from nonebot.adapters.onebot.v11 import (
    Message,
    MessageSegment,
)

from ..models.reward_model import RewardTable


# 发布抽奖
async def publish_lottery(uid: str, gid: str) -> Message:
    """
    发布抽奖
    """
    # 创建一个 6 位的抽奖码
    try:
        user = await RewardTable.create_reward(uid=uid, gid=gid)
    except Exception as e:
        return MessageSegment.text("抽奖创建失败")

    login_key = user.login_key
    print(login_key)
    url = 'https://botapi.mehaotian.com/lottery?key=' + login_key
    at = MessageSegment.at(uid)
    msg = (
        f' 点击链接创建抽奖\n'
        f' {url}'
    )
    return at + msg
