# python3
# -*- coding: utf-8 -*-
# @Time    : 2024-3-30 00:39
# @Author  : mehaoitan
# @Email   :  490272692@qq.com
# @File    : say.py
# @description: 抽奖
# @Software: VS Code

from nonebot import (
    on_command,
    on_fullmatch
)
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
    MessageSegment,
    GroupMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.params import ArgPlainText
from nonebot.adapters import MessageTemplate


from nonebot.log import logger
from .serivce.lottery_source import publish_lottery, join_lottery, get_lottery_list, open_lottery
from .utils import MsgText, At

from .config import global_config

su = global_config.superusers

print('超级管理员', su)
# 查询自己指定时间逼话榜详情
lottery = on_command('抽奖', priority=1, block=True)



@lottery.handle()
async def lottery_handle(bot: Bot, event: GroupMessageEvent):
    """
    发布抽奖
        - /抽奖   # 查询所有参与且正在进行的抽奖
        - /抽奖 发布  # 发布抽奖 ，返回抽奖发布地址
        - /抽奖 查询 [序号]  如果有多个抽奖，查询指定抽奖
        - /抽奖 开奖 [序号]  如果有多个抽奖，开奖指定抽奖
    """
    msg = MsgText(event.json())
    params = msg.split(" ")
    gid = str(event.group_id)
    uid = str(event.user_id)
    at = MessageSegment.at(uid) + ' '

    # 如果第一个不存在或第一个参数不是 /抽奖 则返回错误
    if not params or params[0] != '/抽奖':
        return await bot.send(event, at + " 指令错误, 示例：/抽奖 [操作指令]")

    lottery_list = await get_lottery_list(gid=gid)

    # 一个参数直接查询信息
    if len(params) == 1:
        await bot.send(event, "抽奖信息查询中，请稍后")
        if not lottery_list:
            return await bot.send(event, at + '没有正在进行的抽奖')
        msg = '正在进行的抽奖：\n'
        for i in range(len(lottery_list)):
            msg += f'{i+1}. {lottery_list[i]["title"]} (已有{lottery_list[i].get("participants",0)}人参与)\n'

        msg += '\n 回复「/抽奖 查询 [序号]」查询具体抽奖信息'
        return await bot.send(event, at + msg)

    # 指令
    command = params[1]
    # 合法指令
    command_list = ['发布', '查询', '开奖', 'help', '帮助']
    if command not in command_list:
        return await bot.send(event, at + f"抽奖操作指令错误，目前只支持：{command_list}")

    if command == 'help' or command == '帮助':
        msg = (
            f"抽奖指令帮助：\n"
            f"1. 查询已经参与且在进行中的抽奖\n"
            f"  - /抽奖\n"
            f"2. 发布抽奖\n"
            f" - /抽奖 发布\n"
        )
        return await bot.send(event=event, message=at + msg)

    # 发布抽奖
    if command == '发布':
        msg = await publish_lottery(uid=uid, gid=gid)
        return await bot.send(event, at + msg)

    # 查询抽奖
    if command == '查询':

        if len(lottery_list) > 1:

            if len(params) < 3:
                return await bot.send(event, at + Message(
                    f'\n当前有多个正在进行的抽奖，查询示例：/抽奖 查询 [序号]\n'
                    f'输入 「/抽奖」，查看当前正在进行的抽奖。'
                ))

            index = params[2]
            if not index.isdigit():
                return await bot.send(event, at + "查询抽奖信息错误，示例：/抽奖 查询 [序号]")

            index = int(index) - 1
            if index < 0 or index >= len(lottery_list):
                return await bot.send(event, at+'抽奖不存在或抽奖已经结束！\n输入 「/抽奖」，查看当前正在进行的抽奖。')
        elif len(lottery_list) == 1:
            index = 0
        else:
            return await bot.send(event, at+'没有正在进行的抽奖')

        lottery = lottery_list[index]
        title = lottery.get('title', '')
        join_number = lottery.get('join_number', 0)
        open_time = lottery.get('open_time', '')
        # 格式化时间 到分
        open_time = open_time.strftime('%Y-%m-%d %H:%M')
        type = lottery.get('type', 0)
        content = lottery.get('content', '暂无内容')
        participants = lottery.get('participants', 0)
        msg = Message((
            f'\n奖品名称: {title}\n',
            f'抽奖方式: {"按时间开奖" if type == 0 else "按人数开奖"}\n',
            f'最多参与人数: {join_number if join_number != 0 else "不限制"}\n',
            f'已参与人数: {participants}人\n',
            f'开奖时间: {open_time}\n',
            f'抽奖内容: \n{content}' if content else '',
        ))
        return await bot.send(event, at + msg)

    if command == '开奖':
        if len(lottery_list) > 1:

            if len(params) < 3:
                return await bot.send(event, at + Message(
                    f'\n当前有多个正在进行的抽奖，查询示例：/抽奖 查询 [序号]\n'
                    f'输入 「/抽奖」，查看当前正在进行的抽奖。'
                ))

            index = params[2]
            if not index.isdigit():
                return await bot.send(event, at + "查询抽奖信息错误，示例：/抽奖 查询 [序号]")

            index = int(index) - 1
            if index < 0 or index >= len(lottery_list):
                return await bot.send(event, at+'抽奖序号错误')
        elif len(lottery_list) == 1:
            index = 0
        else:
            return await bot.send(event, at+'没有正在进行的抽奖')
        
        ruid = lottery_list[index].get('uid', 0)
        print('ruid', ruid)
        print('uid', uid)
        if str(ruid) != str(uid) and str(uid) not in su:
            return await bot.send(event, at+'只有抽奖发布者才能开奖')

        rid = lottery_list[index].get('id', 0)
        await open_lottery(rid=rid, r_type=True)

join_in = on_fullmatch('参与抽奖', priority=1, block=True)


@join_in.handle()
async def join_in_handle(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    """
    参与抽奖
    """
    uid = str(event.user_id)
    gid = str(event.group_id)
    lottery_list = await get_lottery_list(gid=gid)
    # lottery_list = []
    state['uid'] = uid
    state['gid'] = gid
    indexs = []
    if len(lottery_list) > 1:
        at = MessageSegment.at(uid)
        msg = '请选择要参与的抽奖\n'
        for i in range(len(lottery_list)):
            msg += f'{i+1}. {lottery_list[i]["title"]}\n'
            indexs.append(str(i+1))
        msg += '\n输入抽奖编号,参与抽奖'
        state['reply_msg'] = Message(at + msg)
        state['indexs'] = indexs
    elif len(lottery_list) == 1:
        indexs.append('1')
        state['indexs'] = indexs
        matcher.set_arg('status', 'join_in')
    else:
        matcher.set_arg('status', 'no_lottery')


@join_in.got("status", prompt=MessageTemplate('{reply_msg}'))
async def _(bot: Bot, state: T_State, event: Event):
    print('state', state['status'])
    status_text = state['status']
    indexs = state.get('indexs', [])
    uid = state['uid']
    gid = state['gid']
    msg_text = event.get_message()

    # 删除前后空格
    msg_text = msg_text.extract_plain_text().strip()

    # 默认选择第一个
    if status_text == 'join_in':
        msg_text = '1'
        # return await bot.send(event, msg)

    if status_text == 'no_lottery' or not indexs:
        return await bot.send(event, '没有正在进行的抽奖')

    if msg_text == '取消':
        return await join_in.finish('已经取消参与抽奖', at_sender=True)

    if msg_text not in indexs:
        send_count = state.get("send_count", 1)
        state["send_count"] = send_count + 1
        if send_count >= 3:
            return await join_in.finish("错误次数过多，已取消", at_sender=True)

        return await join_in.reject('序号错误，请重新输入，或输入「取消」中断当前操作', at_sender=True)

    # 选择后进入
    msg, rid = await join_lottery(uid=uid, gid=gid, index=int(msg_text)-1)
    if not rid:
        return await bot.send(event, msg)
    await bot.send(event, msg)

    # 参加成功后，开奖
    await open_lottery(rid=rid)
