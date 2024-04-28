from nonebot.log import logger
from nonebot_plugin_tortoise_orm import add_model
from ..config import global_config

db_url = global_config.db_url

add_model(__name__, db_name='roulettedb', db_url=db_url)

try:
    from . import roulette_game
    RouletteGameTable = roulette_game.RouletteGameTable
    logger.success('RouletteGameTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'RouletteGameTable 模型加载失败: {e}')


try:
    from . import roulette_player
    RoulettePlayerTable = roulette_player.RoulettePlayerTable
    logger.success('RoulettePlayerTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'RoulettePlayerTable 模型加载失败: {e}')

try:
    from . import roulette_card
    RouletteCardTable = roulette_card.RouletteCardTable
    logger.success('RouletteCardTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'RouletteCardTable 模型加载失败: {e}')




