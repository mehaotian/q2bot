# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : say.py
# @description: 逼话排行榜
# @Software: VS Code

import re
import time
from nonebot import (
    on_message,
    on_fullmatch,
    on_notice,
    on_regex
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    NoticeEvent
)
from nonebot.typing import T_State
from nonebot.log import logger
from .serivce.say_source import get_say_list, save_user_say, get_user_say

# 监听用户消息
run_say = on_message(priority=0, block=False)

# 消息撤回
recall_run = on_notice(priority=1, block=False)

# 逼话排行榜
say = on_fullmatch("逼话排行榜", priority=1, block=False)

# 查询自己指定时间逼话榜详情
query_me_reg = r"(今日|昨天|前天|本月|上月|今年|去年|全部)逼话"
query_me = on_regex(query_me_reg, priority=1, block=False)


@say.handle()
async def say_handle(bot: Bot, event: GroupMessageEvent):
    # # 用户ID
    # user_id = str(event.user_id)
    # 获取群组ID
    group_id = str(event.group_id)

    await bot.send(event=event, message="今日逼话排行榜正在准备中，请稍后...")

    msg = await get_say_list(group_id)
    await bot.send(event=event, message=msg)


@run_say.handle()
async def saying_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    # 获取经验
    # msg = await game.add_exp(event)
    # 获取用户消息
    message = event.get_message()
    msgdata = message.extract_plain_text().strip()

    imagesCount = 0
    facesCount = 0
    replyCount = 0
    at_user_ids = []
    textCount = len(msgdata)
    # 每条记录
    total_count = 0
    for msg in message:
        print('type', msg.type)
        print('data', msg.data)
        if msg.type == "reply":
            replyCount += 1
        if msg.type == "image":
            imagesCount += 1
        if msg.type == "face":
            facesCount += 1
        if msg.type == "at":
            user_id = msg.data.get('qq', None)
            print('user_id', user_id)
            if user_id:
                # 如果存在则不插入
                if user_id not in at_user_ids:
                    at_user_ids.append(user_id)
            print('at_user_ids', at_user_ids)
            

    total_count += 1

    user_id = str(event.user_id)
    group_id = str(event.group_id)
    sender = event.sender

    # 构建消息体
    data = {
        'image_count': imagesCount,
        'face_count': facesCount,
        'reply_count': replyCount,
        'at_count': len(at_user_ids),
        'text_count': textCount,
        'total_count': total_count
    }

    await save_user_say(user_id, group_id, sender, data)


@query_me.handle()
async def query_me_handle(bot: Bot, event: GroupMessageEvent, state: T_State):
    # 获取消息内容
    text = event.message.extract_plain_text().strip()
    print(text)

    # 获取群组ID
    group_id = str(event.group_id)

    # 获取用户ID
    user_id = str(event.user_id)

    # 获取匹配的月份或日期
    match = re.match(query_me_reg, text)
    logger.debug(f'match：{match}')
    if match:
        date = match.group(1)
        # await get_says(date_str=date, group_id=group_id, user_id=user_id)
        await bot.send(event=event, message=f"{date}逼话正在准备中，请稍后...")
        msg = await get_user_say(date_str=date, user_id=user_id, group_id=group_id)

        # 查询指定时间的逼话排行榜
        await bot.send(event=event, message=msg)


@recall_run.handle()
async def recall_handle(bot: Bot, event: NoticeEvent):
    # message = event.get_message()
    # 被操作
    user_id = str(event.user_id)
    # 操作者
    operator_id = str(event.operator_id)

    message_type = event.notice_type
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    recall_count = 0

    if message_type == "group_recall":
        if user_id == operator_id:
            recall_count += 1
            data = {
                "recall_count": recall_count
            }
            user = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
            print('user', user)
            await save_user_say(user_id=user_id, group_id=group_id, sender=user, data=data)
