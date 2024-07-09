

import os
import random
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    Message,
)
from nonebot.typing import T_State

from nonebot.plugin import PluginMetadata
from .config import Config, document_url, local_pad_id
from .download_excel import TengXunDocument
from .excel2json import getJson

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_play_game",
    description="玩游戏",
    usage="",
    type="application",
    homepage="",
    config=Config,
    supported_adapters={"~onebot.v11"},
)


# 更新 excel
update_excel = on_command("更新游戏文档", priority=5, block=False)
# 更新 excel
update_cookie = on_command("更新cookie", priority=5, block=False)
# 查询 excel
query_excel = on_command("鹅子屋", priority=5, block=False)
# 随个游戏
play_game = on_command("随个游戏", priority=5, block=False)
# 今晚玩啥
play_here = on_command("今晚玩它", priority=5, block=False)

ezi_choujiang = on_command("抽奖统计", priority=5, block=False)


@update_excel.handle()
async def _(bot: Bot, event: Event):
    # 获取当前执行文件所在的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # 构建要读取的文件的路径
    file_path = os.path.join(current_directory, 'cookie.txt')
    with open(file_path, 'r', encoding='utf-8') as file:
        # 读取文件内容
        cookie_value = file.read()
    tx = TengXunDocument(document_url, local_pad_id, cookie_value)

    await bot.send(event, "正在更新游戏文档，请稍等...")

    # 导出文件任务url
    export_excel_url = f'https://docs.qq.com/v1/export/export_office'
    
    # 获取导出任务的操作id
    operation_id = tx.export_excel_task(export_excel_url)

    if not operation_id:
        await update_excel.finish("更新文档失败，请检查cookie是否过期")

    check_progress_url = f'https://docs.qq.com/v1/export/query_progress?operationId={operation_id}'
    file_name = f'鹅子屋.xlsx'
    tx.download_excel(check_progress_url, file_name)

    await update_excel.finish("更新游戏文档成功")


@update_cookie.got("event",  prompt='请输入 cookie，取消请回复 取消')
async def handle_divorce(state: T_State, event: Event):
    msgdata = event.get_message()
    msgdata = msgdata.extract_plain_text().strip()

    if msgdata == "取消":
        await update_cookie.finish("已取消更新cookie", at_sender=True)
    else:
        # 获取当前执行文件所在的目录
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # 构建要读取的文件的路径
        file_path = os.path.join(current_directory, 'cookie.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            # 将修改后的内容写回文件
            file.write(msgdata)

        await update_cookie.finish('cookie 更新完成', at_sender=True)


@query_excel.handle()
async def _(bot: Bot, event: Event):
    url = document_url
    msg = (
        f'鹅子屋游戏文档：\n'
        f'{url}'
    )

    await query_excel.finish(Message(msg))

    # json_data = getJson()
    # if json_data is not None:
    #     # 在这里使用 JSON 数据进行进一步处理
    #     print(json_data)
    #     await query_excel.finish("查询成功")
    # else:
    #     # 如果 JSON 数据为 None，可以根据需要采取其他措施
    #     await query_excel.finish("获取失败，请使用 「更新游戏文档」命令更新文档")

@ezi_choujiang.handle()
async def _(bot: Bot, event: Event):
    url = 'https://docs.qq.com/sheet/DQXpTb3hFaWdYWVZP'
    msg = (
        f'抽奖统计：\n'
        f'{url}'
    )

    await query_excel.finish(Message(msg))

@play_game.handle()
async def _(bot: Bot, event: Event):
    json_data = getJson()

    if not json_data:
        await play_game.finish("指令执行失败，原因是发生错误，请联系大鹅检查")

    json_data = [item for item in json_data if item.get('游戏名称', None) != None]
    if json_data is not None:
        # 随机一条数据
        data = random.choice(json_data)
        print(data)
        msg = Message()
        for key in data:
            if key != '今晚玩它':
                msg += f'{key}: {data[key]}\n'

        await play_game.finish(msg)
    else:
        # 如果 JSON 数据为 None，可以根据需要采取其他措施
        await play_game.finish("指令执行失败，原因是文档cookie失效，请联系白鹅更新cookie")


@play_here.handle()
async def _(bot: Bot, event: Event):
    json_data = getJson()
    json_data = [item for item in json_data if item.get('今晚玩它', None) == '是']

    if json_data is not None:
        # 随机数据中 key 为 今晚玩它的值是 True 的数据
        if len(json_data) == 0:
            await play_here.finish((
                f'你还没有勾选药丸的游戏 ，请在鹅子屋中勾选后再来吧，记得更新文档哦～\n'
                f'鹅子屋游戏文档：\n'
                f'{document_url}'
            ))
        # 在这里使用 JSON 数据进行进一步处理
        else:
            data = random.choice(json_data)
            print(data)
            msg = Message()
            for key in data:
                if key != '今晚玩它':
                    msg += f'{key}: {data[key]}\n'
            await play_here.finish(msg)
    else:
        # 如果 JSON 数据为 None，可以根据需要采取其他措施
        await play_here.finish("指令执行失败，原因是文档cookie失效，请联系白鹅更新cookie")
