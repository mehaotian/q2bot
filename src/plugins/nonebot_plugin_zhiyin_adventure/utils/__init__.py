# python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/16 10:15
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : utils.py
# @Software: PyCharm
import asyncio
import base64
import datetime
import json
import os
import random
import re
from typing import Union, Optional

import httpx
import nonebot
from nonebot import logger
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, ActionFailed, Bot
from nonebot.matcher import Matcher

from ..config import plugin_config, global_config

su = global_config.superusers
cb_notice = plugin_config.callback_notice


def At(data: str) -> Union[list[str], list[int], list]:
    """
    检测at了谁，返回[qq, qq, qq,...]
    包含全体成员直接返回['all']
    如果没有at任何人，返回[]
    :param data: event.json
    :return: list
    """
    try:
        qq_list = []
        data = json.loads(data)
        for msg in data['message']:
            if msg['type'] == 'at':
                if 'all' not in str(msg):
                    qq_list.append(int(msg['data']['qq']))
                else:
                    return ['all']
        return qq_list
    except KeyError:
        return []


def Reply(data: str):
    """
    检测回复哪条消息，返回 reply 对象
    如果没有回复任何人，返回 None
    :param data: event.json()
    :return: dict | None
    """
    try:
        data = json.loads(data)
        if data['reply'] and data['reply']['message_id']:  # 待优化
            return data['reply']
        else:
            return None
    except KeyError:
        return None


def MsgText(data: str):
    """
    返回消息文本段内容(即去除 cq 码后的内容)
    :param data: event.json()
    :return: str
    """
    try:
        data = json.loads(data)
        # 过滤出类型为 text 的【并且过滤内容为空的】
        msg_text_list = filter(lambda x: x['type'] == 'text' and x['data']['text'].replace(' ', '') != '',
                               data['message'])
        # 拼接成字符串并且去除两端空格
        msg_text = ' '.join(map(lambda x: x['data']['text'].strip(), msg_text_list)).strip()
        return msg_text
    except:
        return ''





async def mk(type_, path_, *mode, **kwargs):
    """
    创建文件夹 下载文件
    :param type_: ['dir', 'file']
    :param path_: Path
    :param mode: ['wb', 'w']
    :param kwargs: ['url', 'content', 'dec', 'info'] 文件地址 写入内容 描述信息 和 额外信息
    :return: None
    """
    if 'info' in kwargs:
        logger.info(kwargs['info'])
    if type_ == 'dir':
        os.mkdir(path_)
        logger.info(f"创建文件夹{path_}")
    elif type_ == 'file':
        if 'url' in kwargs:
            if kwargs['dec']:
                logger.info(f"开始下载文件{kwargs['dec']}")
            async with httpx.AsyncClient() as client:
                try:
                    r = await client.get(kwargs['url'])
                    if mode[0] == 'w':
                        with open(path_, 'w', encoding='utf-8') as f:
                            f.write(r.text)
                    elif mode[0] == 'wb':
                        with open(path_, 'wb') as f:
                            f.write(r.content)
                    logger.info(f"下载文件 {kwargs['dec']} 到 {path_}")
                except:
                    logger.error('文件下载失败!!!')
        else:
            if mode:
                with open(path_, mode[0]) as f:
                    f.write(kwargs['content'])
                logger.info(f"创建文件{path_}")
            else:
                raise Exception('mode 不能为空')
    else:
        raise Exception('type_参数错误')


async def banSb(bot: Bot, gid: int, ban_list: list, time: int = None, scope: list = None):
    """
    构造禁言
    :param gid: 群号
    :param time: 时间（s)
    :param ban_list: at列表
    :param scope: 用于被动检测禁言的时间范围
    :return:禁言操作
    """
    if 'all' in ban_list:
        yield bot.set_group_whole_ban(
            group_id=gid,
            enable=True
        )
    else:
        if time is None:
            if scope is None:
                time = random.randint(plugin_config.ban_rand_time_min, plugin_config.ban_rand_time_max)
            else:
                time = random.randint(scope[0], scope[1])
        for qq in ban_list:
            if int(qq) in su or str(qq) in su:
                logger.info(f"SUPERUSER无法被禁言, {qq}")
                # if cb_notice:
                #     await nonebot.get_bot().send_group_msg(group_id = gid, message = 'SUPERUSER无法被禁言')
            else:
                yield bot.set_group_ban(
                    group_id=gid,
                    user_id=qq,
                    duration=time,
                )


async def replace_tmr(msg: str) -> str:
    """
    原始消息简单处理
    :param msg: 消息字符串
    :return: 去除cq码,链接等
    """
    find_cq = re.compile(r"(\[CQ:.*])")
    find_link = re.compile("(https?://.*[^\u4e00-\u9fa5])")
    cq_code = re.findall(find_cq, msg)
    for cq in cq_code:
        msg = msg.replace(cq, '')
    links = re.findall(find_link, msg)
    for link in links:
        msg = msg.replace(link, '')
    return msg


def participle_simple_handle() -> list[str]:
    """
    wordcloud停用词
    """
    prep_ = ['么', '了', '与', '不', '且', '之', '为', '兮', '其', '到', '云', '阿', '却', '个',
             '以', '们', '价', '似', '讫', '诸', '取', '若', '得', '逝', '将', '夫', '头', '只',
             '吗', '向', '吧', '呗', '呃', '呀', '员', '呵', '呢', '哇', '咦', '哟', '哉', '啊',
             '哩', '啵', '唻', '啰', '唯', '嘛', '噬', '嚜', '家', '如', '掉', '给', '维', '圪',
             '在', '尔', '惟', '子', '赊', '焉', '然', '旃', '所', '见', '斯', '者', '来', '欤',
             '是', '毋', '曰', '的', '每', '看', '着', '矣', '罢', '而', '耶', '粤', '聿', '等',
             '言', '越', '馨', '趴', '从', '自从', '自', '打', '到', '往', '在', '由', '向', '于',
             '至', '趁', '当', '当着', '沿着', '顺着', '按', '按照', '遵照', '依照', '靠', '本着',
             '用', '通过', '根据', '据', '拿', '比', '因', '因为', '由于', '为', '为了', '为着',
             '被', '给', '让', '叫', '归', '由', '把', '将', '管', '对', '对于', '关于', '跟',
             '和', '给', '替', '向', '同', '除了']

    pron_ = ['各个', '本人', '这个', '各自', '哪些', '怎的', '我', '大家', '她们', '多少', '怎么', '那么', '那样',
             '怎样', '几时', '哪儿', '我们', '自我', '什么', '哪个', '那个', '另外', '自己', '哪样', '这儿', '那些',
             '这样', '那儿', '它们', '它', '他', '你', '谁', '今', '吗', '是', '乌', '如何', '彼此', '其次', '列位',
             '该', '各', '然', '安', '之', '怎', '夫', '其', '每', '您', '伊', '此', '者', '咱们', '某', '诸位',
             '这些', '予', '任何', '若', '彼', '恁', '焉', '兹', '俺', '汝', '几许', '多咱', '谁谁', '有些', '干吗',
             '何如', '怎么样', '好多', '哪门子', '这程子', '他人', '奈何', '人家', '若干', '本身', '旁人', '其他',
             '其余', '一切', '如此', '谁人', '怎么着', '那会儿', '自家', '哪会儿', '谁边', '这会儿', '几儿', '这么些',
             '那阵儿', '那么点儿', '这么点儿', '这么样', '这阵儿', '一应', '多会儿', '何许', '若何', '大伙儿', '几多',
             '恁地', '谁个', '乃尔', '那程子', '多早晚', '如许', '倷', '孰', '侬', '怹', '朕', '他们', '这么着',
             '那么些', '咱家', '你们', '那么着']

    others_ = ['就', '这', '那', '都', '也', '还', '又', '有', '没', '好', '我', '我的', '说', '去', '点', '不是',
               '就是', '要', '一个', '现在',
               '啥']

    sum_ = prep_ + pron_ + others_
    return sum_


def bytes_to_base64(data):
    return base64.b64encode(data).decode('utf-8')


def json_load(path) -> Optional[dict]:
    """
    加载json文件
    :return: Optional[dict]
    """
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            contents = json.load(f)
            return contents
    except FileNotFoundError:
        return None


def json_upload(path, dict_content) -> None:
    """
    更新json文件
    :param path: 路径
    :param dict_content: python对象，字典
    """
    with open(path, mode='w', encoding='utf-8') as c:
        c.write(json.dumps(dict_content, ensure_ascii=False, indent=2))

async def change_s_title(bot: Bot, matcher: Matcher, gid: int, uid: int, s_title: Optional[str]):
    """
    改头衔
    :param bot: bot
    :param matcher: matcher
    :param gid: 群号
    :param uid: 用户号
    :param s_title: 头衔
    """
    try:
        await bot.set_group_special_title(
            group_id=gid,
            user_id=uid,
            special_title=s_title,
            duration=-1,
        )
        await log_fi(matcher, f"头衔操作成功:{s_title}")
    except ActionFailed:
        logger.info('权限不足')



async def vio_level_init(path_user, uid, this_time, label, content) -> None:
    with open(path_user, mode='w', encoding='utf-8') as c:
        c.write(json.dumps({uid: {'level': 0, 'info': {this_time: [label, content]}}}, ensure_ascii=False))


async def sd(cmd: Matcher, msg, at=False) -> None:
    if cb_notice:
        await cmd.send(msg, at_sender=at)


async def log_sd(cmd: Matcher, msg, log: str = None, at=False, err=False) -> None:
    (logger.error if err else logger.info)(log if log else msg)
    await sd(cmd, msg, at)


async def fi(cmd: Matcher, msg) -> None:
    await cmd.finish(msg if cb_notice else None)


async def log_fi(cmd: Matcher, msg, log: str = None, err=False) -> None:
    (logger.error if err else logger.info)(log if log else msg)
    await fi(cmd, msg)


def copyFile(origin, target):
    with open(origin, "rb") as f, open(target, "wb") as f2:
        f2.write(f.read())