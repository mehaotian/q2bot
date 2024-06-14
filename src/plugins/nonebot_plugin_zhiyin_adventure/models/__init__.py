from nonebot.log import logger
from nonebot_plugin_tortoise_orm import add_model
from ..config import global_config

db_url = global_config.db_url

add_model(__name__, db_name='zhiyindb', db_url=db_url)

try:
    from . import zhiyin_game
    ZyGameTable = zhiyin_game.RouletteGameTable
    logger.success('ZyGameTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'ZyGameTable 模型加载失败: {e}')


try:
    from . import zhiyin_player
    ZyPlayerTable = zhiyin_player.RoulettePlayerTable
    logger.success('ZyPlayerTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'ZyPlayerTable 模型加载失败: {e}')



