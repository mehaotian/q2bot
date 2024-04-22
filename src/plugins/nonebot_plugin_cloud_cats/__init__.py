
import locale
from nonebot import require
require("nonebot_plugin_tortoise_orm")
from nonebot.plugin import PluginMetadata
from .config import Config, global_config
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger
# from . import models
from importlib import import_module

# from .core import (
#     game
# )

import_module('.models', __package__)
import_module('.core', __package__)
# 设置本地化
locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
# db_url = 'postgresql://wuhao:1qaz!QAZ@bot.mehaotian.com:5432/botdb_dev'

__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_cloud_cats",
    description="多功能群管",
    usage=f"",
    type="application",
    homepage="",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 设置定时任务持久化
try:
    cat_scheduler_db_url = global_config.cat_scheduler_db_url
    scheduler.add_jobstore(SQLAlchemyJobStore(
        url=cat_scheduler_db_url), 'catsqljob')
    logger.success('Cat Jobstore 持久化成功')
except Exception as e:
    logger.error(f'Cat Jobstore 持久化失败: {e}')
