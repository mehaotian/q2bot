#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   lottery_source.py
@Time    :   2024/04/16 10:40:49
@Author  :   haotian 
@Version :   1.0
@Desc    :   抽奖操作
'''


from datetime import datetime
import random
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
)
from nonebot import get_bot

from tortoise.functions import Count

from ..models.reward_model import RewardTable
from ..models.user_model import UserTable
from ..models.steam_model import SteamTable
from ..models.join_lottery_model import JoinLotteryTable
from apscheduler.jobstores.base import JobLookupError
from tortoise.exceptions import DoesNotExist
from ..config import web_url
from nonebot import require
try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None
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
    url = f'{web_url}/lottery?key=' + login_key
    msg = (
        f' 点击链接创建抽奖\n'
        f' {url}'
    )
    return msg


# 参与抽奖
async def join_lottery(uid: str, gid: str, index: int) -> Message:
    """
    参与抽奖
    """

    # 必须绑定 steam 才能参与抽奖
    try:
        steam_record = await SteamTable.get(user_id=uid)
    except DoesNotExist:
        return MessageSegment.text("为了避免无效的奖品发放，请先关联 Steam 账号\n请使用 「/steam 绑定 [好友代码]」指令关联"), None
    print('steam_record:', steam_record)

    lottery_list = await get_lottery_list(gid=gid)
    lottery_data = lottery_list[index]
    rid = lottery_data['id']
    at = MessageSegment.at(uid)
    # 抽奖类型
    lottery_type = lottery_data['type']

    # 最多参与人数
    join_number = lottery_data['join_number']
    # 参与人数
    participants = lottery_data.get('participants', 0)
    # 按人数开奖
    if lottery_type == 1:
        if join_number <= participants:
            return at + MessageSegment.text(" 抽奖人数已经满了！"), None
    else:
        if join_lottery != 0 and join_number <= participants:
            return at + MessageSegment.text(" 抽奖人数已经满了！"), None

    open_time = lottery_data['open_time']
    # 格式化时间 保留到分
    open_time = open_time.strftime('%Y-%m-%d %H:%M')
    now = datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M')
    # 开奖时间小于当前时间
    if open_time < now:
        return at+MessageSegment.text(" 已经过了开奖时间"), None

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
                f"已参与人数：{str(len(user_list))}人",
            ]
        )
    msg = at + " " + MessageSegment.text(msg)

    if msg_type == 2:
        return msg, lottery_data['id']
    return msg, None


async def open_lottery(rid: int, r_type=False) -> Message:
    """
    开奖
    参数：
        - rid: 抽奖ID
        - r_type: 是否强制开奖
    """
    bot: Bot = get_bot()
    # 获取抽奖
    lottery_data = await RewardTable.get(id=rid)

    # 获取发布者
    uid = lottery_data.uid
    gid = lottery_data.gid

    join_number = lottery_data.join_number

    # 获取所有抽奖用户
    user_list = await JoinLotteryTable.get_user(rid=rid)

    # 抽奖类型
    lottery_type = lottery_data.type
    # 参与人数
    participants = len(user_list)

    open_time = lottery_data.open_time
    # 格式化时间 保留到分
    open_time = open_time.strftime('%Y-%m-%d %H:%M')
    now = datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M')

    # type = True 为强制开奖
    if not r_type:
        # 不满足开奖时间
        if open_time > now:
            # 按人数开奖
            if lottery_type == 1:
                if join_number > participants:
                    return None
            else:
                return None

    job_id = f"lottery_{rid}"
    try:
        scheduler.remove_job(job_id)
        print(f"任务 {job_id} 已经停止")
    except JobLookupError:
        print(f"任务 {job_id} 已经停止,本次为无效停止")

    # 没有用户参加
    if participants == 0:
        msg = Message((
            f'很遗憾没有人中奖！\n'
            f'抽奖名称：{lottery_data.title} \n'
            f'参与人数：{str(participants)}人\n'
        ))
        # 更新抽奖状态
        lottery_data.status = 2
        await lottery_data.save(update_fields=['status'])
        return await bot.send_group_msg(group_id=int(gid), message=msg)

    # 可以开奖了，超出人数，或者超出时间
    participants = user_list[:join_number]

    # 创建一个列表，包含所有参与者
    lottery_pool = list(participants)

    # winner = random.choice(lottery_pool)
    winner = reset_lottery(winner=None, lottery_pool=lottery_pool)
    if not winner:
        return '没了，一点都没了，所有人都中过一次奖了！'

    at = MessageSegment.at(int(winner.user.user_id))
    at_sender = MessageSegment.at(int(uid))
    msg = (
        f'\n恭喜 {winner.user.nickname} 中奖！\n'
        f'抽奖名称：{lottery_data.title} \n'
        f'参与人数：{str(len(participants))}人\n'
    )
    msg = at + " " + MessageSegment.text(msg) + MessageSegment.text(
        '请联系') + at_sender + MessageSegment.text('领取奖品！')

    # 更新抽奖状态
    lottery_data.status = 2
    await lottery_data.save(update_fields=['status'])

    # 更新用户中奖状态
    winner.status = 1
    await winner.save(update_fields=['status'])

    return await bot.send_group_msg(group_id=int(gid), message=msg)


def reset_lottery(lottery_pool):
    """
    重置抽奖
    """
    while True:
        winner = random.choice(lottery_pool)
        if winner.status != 1:
            return winner

        # 如果所有的winner的status都为1，跳出循环
        if all(w.status == 1 for w in lottery_pool):
            break

    return None


def get_lottery_condition(params, lottery_list, command):
    """
    获取抽奖条件
    参数：
        - params: 参数
        - lottery_list: 抽奖列表
        - command: 指令
    返回：
        - index: 抽奖序号
        - msg: 错误信息
    """
    msg = ''

    if len(params) > 2:
        index = params[2]
    else:
        index = '0'

    if len(lottery_list) > 1:
        if len(params) < 3:
            msg = Message(
                f'\n当前有多个正在进行的抽奖，查询示例：/抽奖 {command} [序号]\n'
                f'输入 「/抽奖」，查看当前正在进行的抽奖。'
            )
            return index, msg
        if not index.isdigit():
            msg = f"查询抽奖信息错误，示例：/抽奖 {command} [序号]"
            return index, msg
        index = int(index) - 1
        if index < 0 or index >= len(lottery_list):
            msg = '抽奖序号错误'
            return index, msg
    elif len(lottery_list) == 1:
        index = 0
    else:
        msg = '没有正在进行的抽奖'

    return index, msg


async def close_lottery(rid: int):
    # 获取抽奖
    if lottery_data := await RewardTable.get(id=rid):
        lottery_data.status = 2
        await lottery_data.save(update_fields=['status'])
        msg = Message((
            f'抽奖已经结束！\n'
            f'抽奖名称：{lottery_data.title} \n'
        ))
    else:
        msg = MessageSegment.text("抽奖不存在！")
    return msg


async def get_lottery_list(gid: str) -> list:
    """
    获取抽奖列表
    """
    # 获取存在且有效的抽奖信息
    # rewards = await RewardTable.filter(gid=gid, status=1).values()
    rewards = await RewardTable.filter(gid=gid, status=1).annotate(participants=Count('reward')).values(
        'id',
        'uid',
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
    return rewards


async def get_lottery_history(event, gid: str, params) -> list:
    """
    获取抽奖历史列表
    """
    if len(params) == 3:
        count = params[2]

        if not count.isdigit():
            msg = f"第三个参数应该为数字\n示例：/抽奖 历史 [查询条数，默认10]"
            return msg, 0
    else:
        count = 10

    count = int(count)
    if count > 50:
        msg = f"只能查询最近50条抽奖"
        return msg, 0

    rewards = await RewardTable.filter(gid=gid).annotate(participants=Count('reward')).order_by('-created_at').limit(count)

    if not rewards or len(rewards) == 0:
        return '没有抽奖历史', 0

    msg = MessageSegment.text('')

    index = 0
    if len(rewards) > 10:
        index = 1
        content = [{
            "type": "node",
            "data": {
                "name": "抽奖历史",
                "uin": str(event.self_id),
                "content": MessageSegment.text(
                    f"回复「/抽奖 查询 [序号]」查询具体抽奖信息"
                )
            }
        }]
        for i in range(len(rewards)):
            reward = rewards[i]
            if reward.status == 0:
                status_txt = '未开始'
            elif reward.status == 1:
                status_txt = '进行中'
            else:
                status_txt = '已结束'
            user = await UserTable.get_user(user_id=reward.uid, group_id=gid)
            msg = MessageSegment.text(
                f"抽奖序号：{i+1}\n"
                f"抽奖名称：{reward.title}\n"
                f"发起人：{user.nickname}\n"
                f"抽奖状态：{status_txt}\n"
                f"参与人数：{reward.participants}\n"
                # f"开奖时间：{reward.open_time.strftime('%Y-%m-%d %H:%M')}\n"
                # f"创建时间：{reward.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            )
            content.append({
                "type": "node",
                "data": {
                    "name": "抽奖历史",
                    "uin": str(event.self_id),
                    "content": msg
                }
            })
        return content, index
    else:
        for i in range(len(rewards)):
            reward = rewards[i]

            if reward.status == 0:
                status_txt = '未开始'
            elif reward.status == 1:
                status_txt = '进行中'
            else:
                status_txt = '已结束'
            user = await UserTable.get_user(user_id=reward.uid, group_id=gid)
            msg += MessageSegment.text(
                f"{i+1}. {reward.title}({status_txt})\n"
                f"发起人：{user.nickname}\n"
                f"------------------\n"
            )

        msg += MessageSegment.text('\n回复「/抽奖 查询 [序号]」查询具体抽奖信息')
        return msg, index


async def get_lottery_history_detail(event, gid, params):
    if len(params) == 3:
        count = params[2]

        if not count.isdigit():
            return f"第三个参数应该为数字\n示例：/抽奖 历史 [查询条数，默认10]", 0
    else:
        return '请输入历史抽奖序号\n查询示例：/抽奖 历史 [条数｜无]', 0

    count = int(count)

    if count > 50:
        return '只能查询最近50条抽奖', 0

    # 先获取最近的50条
    rewards = await RewardTable.filter(gid=gid).annotate(participants=Count('reward')).order_by('-created_at').limit(50)

    if not rewards or len(rewards) == 0:
        return '没有抽奖历史', 0

    try:
        reward = rewards[count-1]
    except IndexError:
        return '未找到对应的抽奖记录', 0

    if not reward:
        return '未找到对应的抽奖记录', 0

    users = await JoinLotteryTable.get_user(rid=reward.id)

    winner = [user for user in users if user.status == 1]
    winner_name = winner[0].user.nickname if winner else '无人参与'

    msg = MessageSegment.text(
        f"抽奖名称：{reward.title}\n"
        f"中奖人：{winner_name}\n"
        f"参与人数：{reward.participants}\n"
        f"开奖时间：{reward.open_time.strftime('%Y-%m-%d %H:%M')}\n"
        f"创建时间：{reward.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"抽奖内容：{reward.content}\n"
    )

    content = [{
        "type": "node",
        "data": {
            "name": "抽奖详情",
            "uin": str(event.self_id),
            "content": msg
        }
    }]

    if users:
        msg = ""
        for i in range(0, len(users), 10):
            group = users[i:i+10]
            for user in group:
                user_name = user.user.nickname
                msg += MessageSegment.text(
                    f"参与群员：{user_name}\n"
                )

            content.append({
                "type": "node",
                "data": {
                    "name": "参与群员",
                    "uin": str(event.self_id),
                    "content": msg
                }
            })
            msg = ""  # 清空消息，为下一组做准备

        return content, 1
    else:
        return msg, 0
