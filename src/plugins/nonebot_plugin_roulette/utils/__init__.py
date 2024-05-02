
import json
from typing import Union
import httpx
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    Message,
)

from io import BytesIO
from nonebot.log import logger
from PIL import Image
from ..config import cache_directory



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