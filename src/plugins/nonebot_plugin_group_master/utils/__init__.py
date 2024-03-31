
import httpx
import os
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