# 如果缓存文件夹不存在，则创建一个
# os.makedirs(cache_directory, exist_ok=True)
# cache_path = os.path.join(cache_directory, avatar_name)

import nonebot
from nonebot import (
    on_command,
)
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from .utils import init, switcher_integrity_check, switcher_handle


driver = nonebot.get_driver()

switcher = on_command('开关', priority=1, block=True,
                      permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@driver.on_bot_connect
async def _(bot: nonebot.adapters.Bot):
    await init()
    await switcher_integrity_check(bot)


@switcher.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    user_input_func_name = str(args)
    try:
        await switcher_handle(gid, matcher, user_input_func_name)
    except KeyError:
        await switcher_integrity_check(bot)
        await switcher_handle(gid, matcher, user_input_func_name)
