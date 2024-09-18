
import locale
from nonebot import require
from nonebot.plugin import PluginMetadata
from .config import Config,global_config
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger
from .config import global_config

from . import (
    welcome,
    say,
    steam,
    lottery,
    group_admin,
    xhh_admin
)


# 设置本地化
locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')

scheduler_db_url = global_config.scheduler_db_url
# db_url = 'postgresql://wuhao:1qaz!QAZ@bot.mehaotian.com:5432/botdb_dev'
print("scheduler_db_url ----- :",scheduler_db_url)
require("nonebot_plugin_tortoise_orm")


__plugin_meta__ = PluginMetadata(
    name="nonebot_plugin_group_master",
    description="多功能群管",
    usage=f"",
    type="application",
    homepage="",
    config=Config,
    supported_adapters={"~onebot.v11"},
)

# 设置定时任务持久化
try:
    scheduler.add_jobstore(SQLAlchemyJobStore(url=scheduler_db_url), 'default')
    logger.success('Jobstore 持久化成功')
except Exception as e:
    logger.error(f'Jobstore 持久化失败: {e}')