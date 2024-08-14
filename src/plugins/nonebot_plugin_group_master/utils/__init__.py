
import json
import re
from typing import Optional, Union
import httpx
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import nonebot
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    Message,
)

from io import BytesIO
from nonebot.log import logger
from PIL import Image
from ..config import cache_directory
from .txt2img import txt2img


admin_funcs = ['签到','逼话榜','轮盘赌','抽奖','steam','答案之书']

 # 如果缓存文件夹不存在，则创建一个
os.makedirs(cache_directory, exist_ok=True)
group_cache_directory = cache_directory / '群功能开关配置'
os.makedirs(group_cache_directory, exist_ok=True)
switcher_path = group_cache_directory / '开关配置.json'


words_blacklist_directory = cache_directory / '禁用词'
os.makedirs(words_blacklist_directory, exist_ok=True)
words_blacklist_path = words_blacklist_directory / '禁用词配置.json'

async def init():
    """
    初始化
    """
    if not switcher_path.exists():
        bots = nonebot.get_bots()
        for bot in bots.values():
            print('bot:',bot)
            logger.info('创建开关配置文件,分群设置,所有功能默认关闭')
            g_list = (await bot.get_group_list())
            switcher_dict = {}
            for group in g_list:
                switchers = {}
                for fn_name in admin_funcs:
                    switchers.update({fn_name: False})
                    # if fn_name in ['签到','steam']:
                    #     switchers.update({fn_name: True})
                switcher_dict.update({str(group['group_id']): switchers})
            with open(switcher_path, 'w', encoding='utf-8') as swp:
                swp.write(f"{json.dumps(switcher_dict,ensure_ascii=False,indent=4)}")
    else:  
        print('开关配置文件已存在') 

async def check_func_status(func_name: str, gid: str) -> bool:
    """
    检查某个群的某个功能是否开启
    :param func_name: 功能名
    :param gid: 群号
    :return: bool
    """
    funcs_status = json_load(switcher_path)
    if funcs_status is None:
        raise FileNotFoundError(switcher_path)
    try:
        return bool(funcs_status[gid][func_name])
    except KeyError:  # 新加入的群
        logger.info(
            f"本群({gid})尚未初始化！将自动初始化：关闭所有开关且设置过滤级别为简单。\n\n请重新发送指令继续之前的操作")
        bots = nonebot.get_bots()
        for bot in bots.values():
            await switcher_integrity_check(bot)
        return False  # 直接返回 false


async def switcher_integrity_check(bot: Bot):
    """
    检查开关配置文件是否完整
    :param bot: Bot 机器人对象
    """
    g_list = (await bot.get_group_list())
    switcher_dict = json_load(switcher_path)
    for group in g_list:
        gid = str(group['group_id'])
        if not switcher_dict.get(gid):
            switcher_dict[gid] = {}
            for func in admin_funcs:
                # if func in ['签到', 'steam']:
                #     switcher_dict[gid][func] = True
                # else:
                switcher_dict[gid][func] = False
        else:
            this_group_switcher = switcher_dict[gid]
            for func in admin_funcs:
                if this_group_switcher.get(func) is None:
                    # if func in ['签到', 'steam']:
                    #     this_group_switcher[func] = True
                    # else:
                    this_group_switcher[func] = False
    json_upload(switcher_path, switcher_dict)


async def switcher_handle(gid, cmd, user_input_func_name):
    for func in admin_funcs:
        if user_input_func_name == func:
            funcs_status = json_load(switcher_path)
            if funcs_status[gid][func]:
                funcs_status[gid][func] = False
                json_upload(switcher_path, funcs_status)
                await cmd.send('已关闭' + user_input_func_name)
            else:
                funcs_status[gid][func] = True
                json_upload(switcher_path, funcs_status)
                await cmd.send('已开启' + user_input_func_name)


async def words_blacklist_init():
    """
    禁用词名单初始化
    """
    if not words_blacklist_path.exists():
        bots = nonebot.get_bots()
        for bot in bots.values():
            logger.info('创建禁用词配置文件,分群设置,默认为空')
            g_list = (await bot.get_group_list())
            words_blacklist_dict = {}
            for group in g_list:
                words_blacklist_dict.update({str(group['group_id']): []})
            with open(words_blacklist_path, 'w', encoding='utf-8') as wbp:
                wbp.write(f"{json.dumps(words_blacklist_dict,ensure_ascii=False,indent=4)}")
    else:
        print('禁用词配置文件已存在')

async def get_words_backlist(gid: str) -> list:
    """
    获取禁用词列表
    :param gid: 群号
    :return: list
    """
    words_blacklist = json_load(words_blacklist_path)
    if words_blacklist is None:
        raise FileNotFoundError(words_blacklist_path)
    try:
        return words_blacklist[gid]
    except KeyError:  # 新加入的群
        logger.info(
            f"本群({gid})尚未初始化！将自动初始化：禁用词列表为空。\n\n请重新发送指令继续之前的操作")
        bots = nonebot.get_bots()
        for bot in bots.values():
            await words_blacklist_init()
        return []
    
async def words_blacklist_handle(gid, cmd, user_input_func_name):
    """
    保存禁用关键词
    """
    words_blacklist = json_load(words_blacklist_path)
    now_words_blacklist = words_blacklist[gid]
    # 如果存在重复的关键词
    if user_input_func_name[0] in now_words_blacklist:
        await cmd.send('已存在该禁用关键词',at_sender=True)
        return
    text = ''
    # 添加全部关键词
    for item in user_input_func_name:
        # 如果包含 &amp; 则转换为 &
        if '&amp;' in item:
            item = item.replace('&amp;', '&')
       
        now_words_blacklist.append(item)
        text += item + ' '
    words_blacklist[gid] = now_words_blacklist
    json_upload(words_blacklist_path, words_blacklist)
    await cmd.send('已添加:' + text,at_sender=True)


def string_to_regex(pattern: str) -> str:
    """
    将字符串转换为正则表达式
    """
    # 转义正则表达式中的特殊字符
    pattern = re.escape(pattern)
    # 将 & 转换为 .*
    pattern = pattern.replace(r'\&', '.*')
    # 将 | 转换为 |
    pattern = pattern.replace(r'\|', '|')
    # 奖 \( 转换为 (
    pattern = pattern.replace(r'\(', '(')
    # 将 \) 转换为 )
    pattern = pattern.replace(r'\)', ')')
    return pattern

async def check_message_legality(gid, cmd,msg) -> bool:
    """
    检查消息是否合法
    """
    words_blacklist_handle = await get_words_backlist(str(gid))
    print('禁用列表：',words_blacklist_handle)
    for pattern in words_blacklist_handle:
        pattern = string_to_regex(pattern)
        print('正则表达式：',pattern)
        if re.search(pattern, msg):
            return False
    return True

async def delete_words_blacklist(gid, cmd, user_input_func_name):
    """
    删除禁用关键词
    """
    words_blacklist = json_load(words_blacklist_path)
    now_words_blacklist = words_blacklist[gid]
    text = ''
    for item in user_input_func_name:
        # 如果包含 &amp; 则转换为 &
        if '&amp;' in item:
            item = item.replace('&amp;', '&')

        print('删除的关键词：',item)
        if item in now_words_blacklist:
            now_words_blacklist.remove(item)
            text += item + ' '
        
    if text == '':
        await cmd.send('不存在该禁用关键词',at_sender=True)
        return
    words_blacklist[gid] = now_words_blacklist
    json_upload(words_blacklist_path, words_blacklist)
    await cmd.send('已删除:' + text,at_sender=True)
        
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
        c.write(json.dumps(dict_content, ensure_ascii=False, indent=4))

def get_start_time(text):
    """
    获取中文日期的指定日期值
    参数：
    - text: 中文日期
    """
    now = datetime.now()
    if text == "今日":
        return datetime(now.year, now.month, now.day)
    elif text == "昨天":
        yesterday = now - timedelta(days=1)
        return datetime(yesterday.year, yesterday.month, yesterday.day)
    elif text == "前天":
        day_before_yesterday = now - timedelta(days=2)
        return datetime(day_before_yesterday.year, day_before_yesterday.month, day_before_yesterday.day)
    elif text == "本周":
        return datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())
    elif text == "上周":
        last_week = now - timedelta(weeks=1)
        return datetime(last_week.year, last_week.month, last_week.day) - timedelta(days=last_week.weekday())
    elif text == "本月":
        return datetime(now.year, now.month, 1)
    elif text == "上月":
        last_month = now - relativedelta(months=1)
        return datetime(last_month.year, last_month.month, 1)
    elif text == "今年":
        return datetime(now.year, 1, 1)
    elif text == "去年":
        return datetime(now.year - 1, 1, 1)
    elif text == "全部":
        return datetime.min
    else:
        return None

def get_end_time(text):
    """
    获取中文日期的指定日期值
    参数：
    - text: 中文日期
    """
    now = datetime.now()
    if text == "今日":
        return datetime(now.year, now.month, now.day) + timedelta(days=1) 
    elif text == "昨天":
        return datetime(now.year, now.month, now.day)
    elif text == "前天":
        return datetime(now.year, now.month, now.day) - timedelta(days=1)
    elif text == "本周":
        # 本周最后一天，59:59：59
        return datetime(now.year, now.month, now.day) + timedelta(days=6 - now.weekday()) + timedelta(days=1) - timedelta(seconds=1)
    elif text == "上周":
        # 上周最后一天，59:59：59
        last_week = now - timedelta(weeks=1)
        return datetime(last_week.year, last_week.month, last_week.day) + timedelta(days=6 - last_week.weekday()) + timedelta(days=1) - timedelta(seconds=1)
    elif text == "本月":
        # 本月最后一天，59:59：59
        return datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
    elif text == "上月":
        # 上个月最后一天，59:59：59
        last_month = now - relativedelta(months=1)
        return datetime(last_month.year, last_month.month + 1, 1) - timedelta(seconds=1)
    elif text == "今年":
        # 今年最后一天，59:59：59
        return datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
    elif text == "去年":
        # 去年最后一天，59:59：59
        return datetime(now.year, 1, 1) - timedelta(seconds=1)
    elif text == "全部":
        return datetime.max
    else:
        return None

async def risk_msg(bot: Bot, event, msg, reply=False, at_sender=False):
    """
    被风控转为 图片发送
    :param bot: Bot 机器人对象
    :param event: 事件
    :param msg: 消息
    :param reply_id: 回复消息 ID
    :param at_id: at 用户 ID
    """
    try:
        # 未封控发送文本
        await bot.send(event=event, message=msg, reply_message=reply, at_sender=at_sender)

    except Exception as err:
        if "retcode=100" in str(err):
            # 风控尝试发送图片
            try:
                img = txt2img(msg=msg)
                img_data = MessageSegment.image(file=img)

                await bot.send(event=event, message=Message(img_data), reply_message=reply, at_sender=at_sender)

            except Exception as err:
                if "retcode=100" in str(err):
                    await bot.send(event, "消息可能被风控,无法完成发送!")
        else:
            await bot.send(event, f"发生了其他错误,报错内容为{err},请检查运行日志!")


def download_image(url, cache_path):
    """
    下载文件并缓存
    """
    # 如果缓存目录不存在，则创建
    if not os.path.exists(cache_directory):
        os.makedirs(cache_directory)

    if os.path.exists(cache_path):
        logger.debug(f"缓存文件已存在: {cache_path}")
        # 如果缓存文件已存在，直接加载并返回
        with open(cache_path, "rb") as file:
            return Image.open(BytesIO(file.read()))
    else:
        logger.debug(f"缓存文件不存在: {cache_path}")
        # 否则下载远程图片，并保存到缓存目录
        response = httpx.get(url)
        if response.status_code == 200:
            with open(cache_path, "wb") as file:
                file.write(response.content)
            return Image.open(BytesIO(response.content))
        else:
            # 处理下载失败的情况
            return None



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