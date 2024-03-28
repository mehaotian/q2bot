import re
from io import BytesIO
from pathlib import Path
from time import time
from typing import Union, Optional, Tuple

from PIL import Image
from littlepaimon_utils import aiorequests
from littlepaimon_utils.files import load_image
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment


# 加载敏感违禁词列表
# ban_word = []
# with open(Path(__file__).parent / 'json_data' / 'ban_word.txt', 'r', encoding='utf-8') as f:
#    for line in f:
#        ban_word.append(line.strip())


class MessageBuild:

    @classmethod
    def Image(cls,
              img: Union[Image.Image, Path, str],
              *,
              size: Optional[Union[Tuple[int, int], float]] = None,
              crop: Optional[Tuple[int, int, int, int]] = None,
              quality: Optional[int] = 100,
              mode: Optional[str] = None
              ) -> MessageSegment:
        """
        说明：
            图片预处理并构造成MessageSegment
            :param img: 图片Image对象或图片路径
            :param size: 预处理尺寸
            :param crop: 预处理裁剪大小
            :param quality: 预处理图片质量
            :param mode: 预处理图像模式
            :return: MessageSegment.image
        """
        if isinstance(img, str) or isinstance(img, Path):
            img = load_image(path=img, size=size, mode=mode, crop=crop)
        else:
            if size:
                if isinstance(size, float):
                    img = img.resize(
                        (int(img.size[0] * size), int(img.size[1] * size)), Image.ANTIALIAS)
                elif isinstance(size, tuple):
                    img = img.resize(size, Image.ANTIALIAS)
            if crop:
                img = img.crop(crop)
            if mode:
                img = img.convert(mode)
        bio = BytesIO()
        img.save(bio, format='JPEG' if img.mode ==
                 'RGB' else 'PNG', quality=quality)
        return MessageSegment.image(bio)


async def get_at_target(msg):
    for msg_seg in msg:
        if msg_seg.type == "at":
            return msg_seg.data['qq']
    return None


def get_message_id(event):
    if event.message_type == 'private':
        return event.user_id
    elif event.message_type == 'group':
        return event.group_id
    elif event.message_type == 'guild':
        return event.channel_id


def replace_all(raw_text: str, text_list: Union[str, list]):
    if not text_list:
        return raw_text
    else:
        if isinstance(text_list, str):
            text_list = [text_list]
        for text in text_list:
            raw_text = raw_text.replace(text, '')
        return raw_text


# 检查该时间戳和当前时间戳相差是否超过n天， 超过则返回True
def check_time(time_stamp, n=1):
    time_stamp = int(time_stamp)
    now = int(time())
    if (now - time_stamp) / 86400 > n:
        return True
    else:
        return False
