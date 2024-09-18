# python3
# -*- coding: utf-8 -*-

import json
import random
from collections.abc import Callable
from pathlib import Path
import re
from urllib.parse import urlparse, parse_qs

from nonebot import logger, on_message, on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment, Bot, GroupMessageEvent
from nonebot.internal.matcher import Matcher

from nonebot.params import EventPlainText
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

from .serivce.xhh_source import bind_user, get_article_info, query_user, get_detail_info
from .utils import At, MsgText, Reply, check_func_status, check_message_legality
from .utils.xhh import get_user_info


def match_url_with_link_id(url_pattern: str) -> Callable[[str], bool]:
    def rule(message: str = EventPlainText()) -> bool:
        parsed_url = urlparse(message)
        if parsed_url.scheme and parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            return "link_id" in query_params and message.startswith(url_pattern.split("?")[0])
        return False

    return rule


look_answer = on_message(rule=match_url_with_link_id(
    "https://api.xiaoheihe.cn/v3/bbs/app/api/web/share"))

share_card = on_message(priority=11, block=False)

xhh_aliases = ['小黑盒', 'xhh', '黑盒']
xhh = on_command('小黑盒', aliases=set(
    xhh_aliases[1:]), priority=1, block=True)


@xhh.handle()
async def xhh_handle(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    msg = MsgText(event.json())
    params = msg.split(" ")
    gid = str(event.group_id)
    uid = str(event.user_id)
    sender = event.sender
    at_user = At(event.json())

    msg = re.sub(' +', ' ', msg)
    params = msg.split(" ")

    if not params or params[0][1:] not in xhh_aliases:
        return await bot.send(event, f"指令错误, 输入 /小黑盒 help 查看帮助")

    # 一个参数直接查询信息
    if len(params) == 1:
        await bot.send(event, "小黑盒信息查询中，请稍后")
        msg = await query_user(user_id=uid)
        return await bot.send(event=event, message=msg)

    # 指令
    command = params[1]
    # 合法指令
    command_list = ['绑定', '查询', '更新', 'help', '帮助', '开奖']
    if command not in command_list:
        # 分享链接  https://api.xiaoheihe.cn/v3/bbs/app/api/web/share?link_id=133815114
        # 是url 并且有link_id

        if command.startswith("https://api.xiaoheihe.cn/v3/bbs/app/api/web/share"):
            parsed_url = urlparse(command)
            query_params = parse_qs(parsed_url.query)
            link_id = query_params.get("link_id", [None])[0]
            if link_id:
                msg = await get_article_info(link_id=link_id, user_id=uid)
                return await matcher.send(MessageSegment.at(uid) + '\n' + msg)
            else:
                return await bot.send(event, "URL 错误，请直接从小黑盒分享中复制链接")
        else:
            return await bot.send(event, f"操作指令错误，目前只支持：{command_list}")

    if command == 'help' or command == '帮助':
        msg = (
            f"小黑盒指令帮助：\n"
            f"1. 绑定「小黑盒ID」 ，所有后续命令都需要本次操作\n"
            f"  - /小黑盒 绑定 「小黑盒ID」\n"
            f"2. 小黑盒基本信息查询，不需要其他指令\n"
            f" - /小黑盒\n"
            f"3. 查询文章信息\n"
            f" - /小黑盒「文章链接」\n"
        )
        return await bot.send(event=event, message=msg)

    # 查询
    if command == '绑定':
        xid = params[2]
        user_res = get_user_info(user_id=xid)
        if user_res is None:
            return await bot.send(event, "未找用户信息,请检查小黑盒ID是否正确")
        try:

            forbid_info = user_res.get('forbid_info', '')
            if forbid_info:
                text = f"绑定失败：{forbid_info}\n"

                return await bot.send(event, MessageSegment.at(uid) + text)

            await bind_user(group_id=gid, user_id=uid, sender=sender, xid=params[2])

            msg_text = (
                f"绑定成功：",
                f"\n小黑盒ID：{xid} \n" if xid else f"\n",
                f"昵称：{user_res.get('username', f'用户{xid}')}\n",
                f"等级：{user_res.get('level_info', {}).get('level', '-')}\n",
            )

            msg = MessageSegment.at(uid) + Message(msg_text)

            await bot.send(event=event, message=msg)
        except Exception as e:
            logger.error(f"绑定小黑盒ID失败: {e}")
            return await bot.send(event, "绑定失败，请稍后再试！")

    if command == '开奖':
        links = ''
        link_data_id = ''
        num = 1
        if len(params) == 2:
            return await bot.send(event, "请输入开奖链接,从文章分享里复制！")
        if len(params) == 3:
            links = params[2]

        if len(params) == 4:
            links = params[2]
            num = params[3]
            if not num.isdigit():
                return await bot.send(event, "请输入正确的数字")
            num = int(num)
            if num == 0:
                return await bot.send(event, "开奖最少一个人")

        if links.startswith("https://api.xiaoheihe.cn/v3/bbs/app/api/web/share"):
            parsed_url = urlparse(links)
            query_params = parse_qs(parsed_url.query)
            link_id = query_params.get("link_id", [None])[0]
            if link_id:
                link_data_id = link_id
            else:
                return await bot.send(event, "URL 错误，请直接从小黑盒分享中复制链接")
        else:
            return await bot.send(event, f"URL 错误，请直接从小黑盒分享中复制链接")

        await get_detail_info(link_id=link_data_id, user_id=uid, matcher=matcher, event=event, bot=bot, num=num)

        # 返回message 发送信息 ，返回数组 进行处理


@look_answer.handle()
async def answersbook(
        bot: Bot, event: MessageEvent, state: T_State, message: str = EventPlainText()
) -> None:
    state["user_id"] = event.user_id
    parsed_url = urlparse(message)
    query_params = parse_qs(parsed_url.query)
    link_id = query_params.get("link_id", [None])[0]

    if link_id:
        state["link_id"] = link_id
        await bot.send(event, f"Link ID: {link_id}")
    else:
        await bot.send(event, "URL 中没有找到 link_id 参数！")


@share_card.handle()
async def share_card_handle(bot: Bot, matcher: Matcher, event: GroupMessageEvent) -> None:
    try:
        data = json.loads(event.json())
        user_id = str(event.user_id)
        for msg in data["message"]:
            if msg["type"] == "json" and msg["data"]:
                msgdata = json.loads(msg["data"]["data"])
                jump_url = msgdata.get("meta", {}).get(
                    "news", {}).get("jumpUrl")
                if jump_url:
                    parsed_url = urlparse(jump_url)
                    link_id = parse_qs(parsed_url.query).get(
                        "link_id", [None])[0]
                    if link_id:
                        msg = await get_article_info(link_id=link_id, user_id=user_id, c_type=True)
                        if msg:
                            return await matcher.send(msg, reply_message=True)
    except Exception as e:
        logger.error(f"处理分享卡片时出错: {e}")
