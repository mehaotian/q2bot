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
from .serivce.lottery_source import publish_lottery, join_lottery, get_lottery_list
from .utils import MsgText, At

# 查询自己指定时间逼话榜详情
lottery = on_command('抽奖', priority=1, block=True)


@lottery.handle()
async def lottery_handle(bot: Bot, event: GroupMessageEvent):
    """
    发布抽奖
        - /抽奖   # 查询所有参与且正在进行的抽奖
        - /抽奖 发布  # 发布抽奖 ，返回抽奖发布地址


    """
    msg = MsgText(event.json())
    params = msg.split(" ")
    gid = str(event.group_id)
    uid = str(event.user_id)

    # 如果第一个不存在或第一个参数不是 /抽奖 则返回错误
    if not params or params[0] != '/抽奖':
        return await bot.send(event, "指令错误, 示例：/抽奖 [操作指令]")

    # 一个参数直接查询信息
    if len(params) == 1:
        await bot.send(event, "抽奖信息查询中，请稍后")
        lottery_list = await get_lottery_list(gid=gid)
        if not lottery_list:
            return await bot.send(event, '没有正在进行的抽奖')
        msg = '正在进行的抽奖：\n'
        for i in range(len(lottery_list)):
            msg += f'{i+1}. {lottery_list[i]["title"]} (已有{lottery_list[i].get("participants",0)}人参与)\n'

        msg += '\n 回复「/抽奖 查询 [序号]」查询具体抽奖信息'
        return await bot.send(event, msg)

    # 指令
    command = params[1]
    # 合法指令
    command_list = ['发布']
    if command not in command_list:
        return await bot.send(event, f"抽奖操作指令错误，目前只支持：{command_list}")

    if command == 'help' or command == '帮助':
        msg = (
            f"抽奖指令帮助：\n"
            f"1. 查询已经参与且在进行中的抽奖\n"
            f"  - /抽奖\n"
            f"2. 发布抽奖\n"
            f" - /抽奖 发布\n"
        )
        return await bot.send(event=event, message=msg)

    # 查询
    if command == '发布':
        msg = await publish_lottery(uid=uid, gid=gid)
        return await bot.send(event, msg)


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
        msg += '输入抽奖编号,参与抽奖'
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
    msg = await join_lottery(uid=uid, gid=gid, index=int(msg_text)-1)
    return await bot.send(event, msg)
