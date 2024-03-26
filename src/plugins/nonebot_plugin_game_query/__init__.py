from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from .utils import hey_box, mes_creater

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="游戏查询",
    description="",
    usage="",
    config=Config,
)


# 小黑盒特惠
game = on_command("test", priority=10, block=True)

# 获取小黑盒特惠消息


@game.handle()
async def _(bot: Bot, event: Event):
    data = hey_box(20)
    content = []

    for item in data:
        content_item = MessageSegment.image(item['图片'])+MessageSegment.text(
            (f"游戏名称：{item['标题']}\n"
             f"原价：{item['原价']}元\n"
             f"史低价：{item['平史低价']}元\n"
             f"当前价：{item['当前价']}元\n"
             f"折扣：-{item['折扣比']}%\n"
             f"是否史低：{item['是否史低']}\n"
             f"是否新史低：{item['是否新史低']}\n"
             f"截止日期：{item['截止日期']}\n"
             f"链接：{item['链接']}")
        )

        content.append({
            "type": "node",
            "data": {
                "name": "游戏特惠",
                "uin": str(event.self_id),
                "content": content_item
            }
        })

    # return
    before_content = [
        {
            "type": "node",
            "data": {
                "name": "游戏特惠",
                "uin": str(event.self_id),
                "content": "数据来源于小黑盒steam促销页面前30条数据"
            }
        }
    ]

    msg_list = [item for item in content]

    before_content.extend(msg_list)
    await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=before_content)
