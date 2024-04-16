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
from tortoise.functions import Count

from ..models.reward_model import RewardTable
from ..models.user_model import UserTable
from ..models.join_lottery_model import JoinLotteryTable


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


# 参与抽奖
async def join_lottery(uid: str, gid: str, index: int) -> Message:
    """
    参与抽奖
    """
    lottery_list = await get_lottery_list(gid=gid)
    lottery_data = lottery_list[index]
    rid = lottery_data['id']
    user = await UserTable.get_user(user_id=uid, group_id=gid)

    # 参与抽奖
    msg_type = await JoinLotteryTable.join(reward_id=rid, uid=user.id)

    if msg_type == 1:
        msg = "您已经参与过本次抽奖了！"
    elif msg_type == 2:
        msg = "参与抽奖成功!"
    else:
        msg = "参与失败，请联系鹅子！"
    # 获取抽奖用户
    user_list = await JoinLotteryTable.get_user_list(rid=rid)

    if msg_type != 3:
        msg += "\n".join(
            [
                f"",
                f"抽奖名称：{lottery_data['title']}",
                f"参与人数：{str(len(user_list))}人",
            ]
        )
    print('参数人数：', len(user_list))

    at = MessageSegment.at(uid)
    return at + " " + MessageSegment.text(msg)


async def get_lottery_list(gid: str) -> list:
    """
    获取抽奖列表
    """
    # 获取存在且有效的抽奖信息
    # rewards = await RewardTable.filter(gid=gid, status=1).values()
    rewards = await RewardTable.filter(gid=gid, status=1).annotate(participants=Count('reward')).values(
        'id',
        'title',
        'content',
        'win_number',
        'join_number',
        'type',
        'status',
        'open_time',  
        'participants'
    )
    if not rewards:
        return []
    print(rewards)
    return rewards
