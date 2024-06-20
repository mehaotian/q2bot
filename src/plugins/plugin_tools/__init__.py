import datetime
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageSegment
)

moyu = on_command("摸鱼日报", priority=9, block=True)
lookworld  = on_command("读世界", priority=9, block=True)


@moyu.handle()
async def moyu_handle(bot: Bot, event: GroupMessageEvent):
    """
    摸鱼日报
    指令：
        - /摸鱼日报
    """
    url = 'https://api.52vmy.cn/api/wl/moyu'
    # image_file = MessageSegment.image(url)
    try:
        image_file = MessageSegment.image(url)
        await bot.send(event=event, message=image_file)

    except Exception as e:
        err_msg = f'获取日报失败，错误信息：{e}'
        await bot.send(event=event, message=err_msg)

@lookworld.handle()
async def lookworld_handle(bot: Bot, event: GroupMessageEvent):
    """
    读世界
    指令：
        - /读世界
    """
    # 将当前时间转为 20240109 格式
    time = datetime.datetime.now().strftime('%Y%m%d')
    url = f'https://jx.iqfk.top/60s/{time}.png'
    try:
        image_file = MessageSegment.image(url)
        await bot.send(event=event, message=image_file)

    except Exception as e:
        err_msg = f'获取日报失败，错误信息：{e}'
        await bot.send(event=event, message=err_msg)