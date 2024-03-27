from nonebot import on_command,on_regex
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from .utils import hey_box, mes_creater

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="游戏查询",
    description="",
    usage="指令：@bot (史低|小黑盒|游戏价格|特惠)",
    config=Config,
)


# 小黑盒特惠查询 ，关键词 史低 小黑盒 游戏价格 特惠
gamereg = "(史低|小黑盒|游戏价格|特惠)"
gamequery = on_regex(pattern = gamereg, rule=to_me(), priority=20, block=True)

# 获取小黑盒特惠消息
@gamequery.handle()
async def _(bot: Bot, event: Event):
    data = hey_box(20)
    content = []
    await bot.send(event= event, message= "正在为您查询，请稍等...")
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

    # 做一个返回错误的处理
    try :
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=before_content)
    except Exception as e:
        await bot.send(event= event, message= "哎呀，出错了，再试一次吧！")
