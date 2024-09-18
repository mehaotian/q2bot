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

from .serivce.xhh_source import bind_user
from .utils import At, MsgText, Reply, check_func_status, check_message_legality
from .utils.xhh import get_article_list, get_user_info


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
        # msg = await query_steam_user(user_id=uid)
        return await bot.send(event=event, message=msg)

    # 指令
    command = params[1]
    # 合法指令
    command_list = ['绑定', '查询', '更新', 'help', '帮助']
    if command not in command_list:
        # 分享链接  https://api.xiaoheihe.cn/v3/bbs/app/api/web/share?link_id=133815114
        # 是url 并且有link_id

        if command.startswith("https://api.xiaoheihe.cn/v3/bbs/app/api/web/share"):
            parsed_url = urlparse(command)
            query_params = parse_qs(parsed_url.query)
            link_id = query_params.get("link_id", [None])[0]
            if link_id:
                await bot.send(event, f"Link ID: {link_id}")
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
        # return await bot.send(event, "查询")

        # steamid = get_steam_id(params[2])

        # print('steamid', steamid)

        # if not steamid:
        #     return await bot.send(event=event, message=MessageSegment.at(uid) + " Steam 好友代码错误")

        # msg = await bind_user(group_id=gid, user_id=uid, sender=sender, xid=params[2])
        user_res = get_user_info(user_id=xid)
        if user_res is None:
            return await bot.send(event, "未找用户信息,请检查小黑盒ID是否正确")
        # try:
                
        await bind_user(group_id=gid, user_id=uid, sender=sender, xid=params[2])

        print("res:", user_res)
        msg = MessageSegment.at(uid) + (
            f"绑定成功：",
            f"\n小黑盒ID：{xid} \n" if xid else f"\n",
            f"昵称：{user_res.get('username',f'用户{xid}')}\n",
            f"等级：{user_res.get('level_info',{}).get('level','-')}\n",
        )

        await bot.send(event=event, message=msg)
        # except Exception as e:
        #     logger.error(f"绑定小黑盒ID失败: {e}")
        #     return await bot.send(event, "绑定失败，请稍后再试！")

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
                        await matcher.send(f"Link ID: {link_id}")
                        return
    except Exception as e:
        logger.error(f"处理分享卡片时出错: {e}")
    await matcher.send("这是一张分享卡片！")

# # 获取小黑盒文章信息
# def startswith_or_endswith(msg: str) -> Callable[[str], bool]:
#     def rule(message: str = EventPlainText()) -> bool:
#         return message.startswith(msg) or message.endswith(msg)
#     return rule

# look_answer = on_message(rule=startswith_or_endswith("黑盒文章"))


# @look_answer.handle()
# async def answersbook(
#     event: MessageEvent, state: T_State, message: str = EventPlainText()
# ) -> None:
#     state["user_id"] = event.user_id
#     if event.reply or message.strip() != "黑盒文章":
#         state["question"] = True


# async def question(bot:Bot ,event: MessageEvent) -> None:
#     pass

# @look_answer.got("question", prompt=Message.template("{user_id:at} 请输入小黑盒文章或图文的URL（文章点击分享，点击复制链接）。"))
# async def question(bot:Bot ,event: MessageEvent) -> None:

#     # 是否回复
#     rp = Reply(event.json())

#     if rp:
#         words = rp['message']
#         print("words:",words)
#         if len(words) == 1:
#             wrod = words[0]
#             if wrod['type'] == 'text':
#                 text = wrod['data']['text']
#                 text = text.strip()
#                 try:
#                     # 解析 URL
#                     parsed_url = urlparse(text)
#                     query_params = parse_qs(parsed_url.query)

#                     # 获取 link_id 参数
#                     link_id = query_params.get("link_id")
#                     if link_id:
#                         link_id = link_id[0]  # 获取第一个值
#                         return await bot.send(event,f"Link ID: {link_id}")
#                     else:
#                         return await look_answer.reject("URL 中没有找到 link_id 参数！")
#                 except Exception as e:
#                     return await look_answer.reject(f"解析 URL 时出错: {e}")

#             return await look_answer.reject("回复格式错误，只能回复链接地址！")
#         return await look_answer.reject("回复信息错误，只能回复自己发布的小黑盒链接地址！")

#     reply_id = event.reply.message_id if event.reply else event.message_id
#     # 获取消息内容
#     text = event.message.extract_plain_text().strip()
#     print("text:",text)
#     await look_answer.finish(
#         MessageSegment.reply(reply_id)
#         + MessageSegment.at(event.user_id)
#         + MessageSegment.text('test')
#     )
