from asyncio import sleep
from os import remove
from httpx import AsyncClient
from nonebot import get_driver, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, PrivateMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from .config import pc

__plugin_meta__ = PluginMetadata(
    name="mcsm api 重启插件",
    description="如名",
    usage=f"""插件命令如下：
{pc.restart_nonebot_cmd}  # 字面意思，仅支持私聊执行
""",
)
driver = get_driver()


# qq机器人连接时执行
@driver.on_bot_connect
async def _(bot: Bot):
    try:
        # with open("restart_info", "r", encoding="utf-8") as r:
        #     target_id, bot_id = r.read().split()

        # if bot.self_id != bot_id:
        #     raise
        target_id = '490272692'
        await sleep(1)
        msg = "报告！喵叽部署完毕！～"
        await bot.send_private_msg(user_id=int(target_id), message=msg)
        remove("restart_info")
    except:
        pass


chongqi = on_fullmatch(pc.restart_nonebot_cmd, permission=SUPERUSER)


@chongqi.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    try:
        await chongqi.send("重启中，请稍后。。。")
        async with AsyncClient(verify=False) as c:
            host = pc.restart_nonebot_host
            gid = pc.restart_nonebot_gid
            uid = pc.restart_nonebot_uid
            key = pc.restart_nonebot_key
            await c.get(
                f"{host}/api/protected_instance/restart?uuid={uid}&remote_uuid={gid}&apikey={key}"
            )
            with open("restart_info", "w", encoding="utf-8") as w:
                # 消息类型  发送目标的号  机器人号
                w.write(f"{event.user_id} {bot.self_id}")
    except Exception as e:
        await chongqi.finish(f"请求失败: {repr(e)}")
