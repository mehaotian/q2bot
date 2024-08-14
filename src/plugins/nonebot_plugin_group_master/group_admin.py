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
from .utils import delete_words_blacklist, get_words_backlist, init, switcher_integrity_check, switcher_handle, words_blacklist_init, words_blacklist_handle, check_message_legality


driver = nonebot.get_driver()

switcher = on_command('开关', priority=1, block=True,
                      permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

words_disable = on_command('禁', priority=1, block=True,
                           permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

# 删除关键字
words_delete = on_command('删', priority=10, block=True,
                            permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

update = on_command('更新配置', priority=1, block=True,
                            permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)

# 查询关键字
words_query = on_command('禁用词', priority=1, block=True)
# test = on_command('test', priority=1, block=True)


@driver.on_bot_connect
async def _(bot: nonebot.adapters.Bot):
    await init()
    await switcher_integrity_check(bot)
    # 初始化禁用词
    await words_blacklist_init()

@update.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    # 初始化禁用词
    await words_blacklist_init()
    await update.finish('更新成功')

@switcher.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    user_input_func_name = str(args)
    try:
        await switcher_handle(gid, matcher, user_input_func_name)
    except KeyError:
        await switcher_integrity_check(bot)
        await switcher_handle(gid, matcher, user_input_func_name)


@words_disable.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    user_input_func_name = str(args)
    user_input_func_name = user_input_func_name.split()
    print(user_input_func_name)
    try:
        await words_blacklist_handle(gid, matcher, user_input_func_name)
    except KeyError:
        await words_blacklist_init()
        await words_blacklist_handle(gid, matcher, user_input_func_name)


@words_delete.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent, args: Message = CommandArg()):
    gid = str(event.group_id)
    user_input_func_name = str(args)
    user_input_func_name = user_input_func_name.split()
    
    try:
        await delete_words_blacklist(gid, matcher, user_input_func_name)
    except KeyError:
        await words_blacklist_init()
        await delete_words_blacklist(gid, matcher, user_input_func_name)


@words_query.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    words = await get_words_backlist(gid=gid)
    if not words:
        await words_query.finish('当前群组没有禁用词')
    words = ', '.join(words)
    await words_query.finish(f'当前群组禁用词: {words}')



# @test.handle()
# async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
#     gid = str(event.group_id)
#     msg = event.message.extract_plain_text().strip()

#     is_ok = await check_message_legality(gid=gid, msg=msg, cmd=matcher)

#     print(is_ok)

#     if not is_ok:
#         await test.finish('命中')
#     await test.finish('未命中')