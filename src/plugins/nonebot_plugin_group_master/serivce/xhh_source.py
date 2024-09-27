#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   steam_source.py
@Time    :   2024/04/14 16:19:23
@Author  :   haotian
@Version :   1.0
@Desc    :   处理 小黑盒 相关数据
'''
from email.policy import default

from nonebot.adapters.onebot.v11 import (
    MessageSegment,
    Message, GroupMessageEvent, Bot
)
from nonebot.internal.matcher import Matcher
from nonebot.log import logger

from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned

from .user_source import create_user
from ..utils.xhh import get_article_list, get_user_info, get_detail, get_comment
from ..models.user_model import UserTable
from ..models.xhh_model import XhhTable
from ..config import plugin_config
from ..text2img.xhh2img import xhh2img


async def bind_user(user_id: str, group_id: str, sender, xid: str) -> MessageSegment:
    # 检查用户，不存在则创建
    # 理论上讲，一个用户只应该存在一个 steam 账户
    await create_user(user_id, group_id, sender)
    user = await XhhTable.create_xhh_info(uid=user_id, xid=xid)
    return user


async def get_article_info(user_id: str, link_id: str, c_type: bool = False):
    """
    获取文章信息
    """
    try:
        user = await XhhTable.get_or_none(user_id=user_id)
        if not user:
            return None if c_type else Message('未绑定小黑盒账号')

        if not user.xhh_id:
            return None if c_type else Message('未绑定小黑盒账号')
        # 获取文章信息
        list = get_article_list(user_id=user.xhh_id, page=1, limit=10)
        res = [item for item in list if str(item['linkid']) == str(link_id)]
        if not res:
            return None if c_type else Message('未找到相关文章,只能查看最近的10篇文章或您查询的是别人的文章。')
        item = res[0]
        backmsg = ''
        if not c_type:
            backmsg += f"{item['title']}\n"

        backmsg += f"| 点击：{item['click']}\n" \
                   f"| 点赞：{item['link_award_num']}\n" \
                   f"| 评论：{item['comment_num']}\n" \
                   f"| 收藏：{item['forward_num']}\n" \
                   f"| 发布于：{item['create_str']}\n"

        return backmsg
    except DoesNotExist:
        return None if c_type else Message('未绑定小黑盒账号')


async def get_detail_info(user_id: str, link_id: str, matcher: Matcher, event: GroupMessageEvent, bot: Bot, num: int):
    user = await XhhTable.get_or_none(user_id=user_id)
    if not user:
        return matcher.send(Message('未绑定小黑盒账号'))

    if not user.xhh_id:
        return matcher.send(Message('未绑定小黑盒账号'))

    share_data = get_detail(link_id=link_id)
    if share_data and share_data.get('share_title'):
        await matcher.send(f'开奖:{share_data.get("share_title")}\n获取参与用户中...')
    page = 1
    result = []

    def loop(page=1):
        comment_data = get_comment(link_id=link_id, page=page)

        comments = comment_data.get('comments', [])
        for item in comments:
            comment = item.get('comment', [])
            data_text = [comment for comment in comment if comment.get('floor_num')]
            data_text = data_text[0] if data_text else None
            if data_text:
                user = data_text.get('user', {})
                if user:
                    result.append({
                        "username": user.get('username'),
                        "floor_num": data_text.get('floor_num'),
                        "avatar": user.get('avatar')
                    })
        total_page = comment_data.get('total_page', 1)
        if page < total_page:
            page += 1
            loop(page)

    loop(page)
    print(len(result))
    is_ok, img_file = xhh2img(data=result, top_text="黑盒", top_title="抽奖", title=f"小黑盒抽奖资格查询")
    print(is_ok)
    if is_ok:
        await matcher.send(MessageSegment.image(file=img_file))
        await matcher.send(f"开始抽奖...")
        # 随机 num 个
        import random
        random.shuffle(result)
        result = result[:num]

        msg = (
            f"本次抽奖{num}人，恭喜中奖用户：\n"
        )
        for item in result:
            msg += f"{item['floor_num']}楼：{item['username']} \n"
        await matcher.send(msg)
    else:
        return await matcher.send(Message("生成失败"))


async def query_user(user_id: str):
    """
    获取用户信息
    """
    try:
        user = await XhhTable.get_or_none(user_id=user_id)
        if not user:
            return Message('未绑定小黑盒账号')

        if not user.xhh_id:
            return Message('未绑定小黑盒账号')

        userdata = get_user_info(user_id=user.xhh_id)

        if not userdata:
            return Message('未找到用户信息,请稍后重试')

        backmsg = f"| 小黑盒ID：{user.xhh_id}\n" \
                  f"| 昵称：{userdata.get('username', f'用户{user.xhh_id}')}\n" \
                  f"| 粉丝：{userdata.get('bbs_info', {}).get('fan_num', '未知')}\n" \
                  f"| 等级：{userdata.get('level_info', {}).get('level', '-')}\n"
        return MessageSegment.at(user_id) + '\n' + backmsg
    except DoesNotExist:
        return Message('获取失败，请稍后重试')
