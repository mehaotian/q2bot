
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageSegment,
    Message,
)
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
