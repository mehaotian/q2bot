from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageSegment
)

moyu = on_command("摸鱼日报", priority=9, block=True)


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
