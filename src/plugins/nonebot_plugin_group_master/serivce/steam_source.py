#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   steam_source.py
@Time    :   2024/04/14 16:19:23
@Author  :   haotian
@Version :   1.0
@Desc    :   处理 steam 相关数据
'''
from steam.steamid import SteamID
from steam.webapi import WebAPI
from nonebot.adapters.onebot.v11 import (
    MessageSegment,
)
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from .user_source import create_user
from ..models.user_model import UserTable
from ..models.steam_model import SteamTable

from ..config import global_config

# 获取 steam key

steam_key = global_config.steam_api_key

try:
    api = WebAPI(steam_key)
except Exception as e:
    print(f"An error occurred: {e}")
    api = None

def get_friend_code(steam_id: str) -> str:
    """
    获取 Steam 好友代码
    :param steam_id: Steam ID
    """
    # 创建 SteamID 对象
    steam_id = SteamID(int(steam_id))
    # 返回 朋友代码
    return steam_id.as_32


def get_steam_id(friend_code: str) -> str:
    """
    获取 Steam ID
    :param friend_code: Steam Code
    """
    # 通用 url 获取 steam_id ，暂时弃用
    # steam_id = SteamID().from_url(url)
    # 通过 好友码 获取 steam_id
    steam_id = SteamID(friend_code)
    # 校验 steam_id 是否合法
    is_steam_id = steam_id.is_valid()

    print('steam_id', is_steam_id)
    if is_steam_id:
        return steam_id

    return None


def get_community_url(steam_id):
    """
    获取 steam 用户主页地址
    参数：
        - steam_id
    """

    steam_id = SteamID(int(steam_id))
    community_url = steam_id.community_url

    return community_url


def get_invite_url(steam_id):
    """
    获取 steam 用户邀请链接
    参数：
        - steam_id
    """

    steam_id = SteamID(int(steam_id))
    invite_url = steam_id.invite_url

    return invite_url


def get_steam_user(steam_id):
    """
    获取 steam 用户信息
    参数:
        - steam_id
    """

    try:

        jsonData = api.call('ISteamUser.GetPlayerSummaries', steamids=steam_id)
        response = jsonData['response']['players'][0]

        print('获取steam用户：', response)

        return response

    except Exception as e: 
        print(f"An error occurred: {e}")
        return None


async def query_steam_user(user_id: str):
    """
    查询用户绑定的 steam 账户
    参数：
        - user_id: 用户ID
    """
    msg = (
        f"未绑定 Steam 账户\n"
        f'请使用 "/steam 绑定 [好友代码]" 指令关联'
    )

    try:
        # 查询用户
        user = await SteamTable.get(user_id=user_id)
    except DoesNotExist:

        return MessageSegment.at(user_id) + " " + msg

    except MultipleObjectsReturned:
        return MessageSegment.at(user_id) + " 找到多个绑定的 Steam 账户,请联系鹅子处理。"

    steam_id = user.steamid
    if not steam_id:
        return MessageSegment.at(user_id) + " " + msg

    player = get_steam_user(steam_id=steam_id)
    player_name = player['personaname'] or player['realname']

    msg = MessageSegment.at(user_id) + (
        f"\nSteam 昵称：{player_name} \n"
        f"好友代码：{get_friend_code(steam_id)}\n"
        f"邀请链接：{get_invite_url(steam_id)}\n"
        f"个人主页：{get_community_url(steam_id)} \n"
    )

    return msg


async def bind_steam_user(user_id: str, group_id: str, sender, steamid):

    # 检查用户，不存在则创建
    # 理论上讲，一个用户只应该存在一个 steam 账户
    await create_user(user_id, group_id, sender)
    msg = None

    recod = await SteamTable.save_steam(user_id, steamid)
    if recod:
        player = get_steam_user(steam_id=steamid)
        if not player:
            return MessageSegment.at(user_id) + " 绑定失败，未找到 Steam 用户"
        
        player_name = player['personaname'] or player['realname']
        if not player_name:
            return MessageSegment.at(user_id) + " 绑定失败，未找到 Steam 用户"

        msg = MessageSegment.at(user_id) + f" 绑定成功，您的 Steam 昵称为：{player_name}\n请确定Steam昵称是否正确，否则请检查好友代码并更正。\n另：请你做个人，别绑别人的steam，一经发现 ，将禁用此功能。"

    return msg
