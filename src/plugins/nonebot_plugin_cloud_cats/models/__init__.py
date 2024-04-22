from nonebot.log import logger
from nonebot_plugin_tortoise_orm import add_model
from ..config import global_config

db_url = global_config.cat_db_url

add_model(__name__, db_name='catdb', db_url=db_url)

try:
    from . import CatGameModel
    CatGameTable = CatGameModel.CatGameTable
    logger.success('CatGameTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'CatGameTable 模型加载失败: {e}')


try:
    from . import CatModel
    CatTable = CatModel.CatTable
    logger.success('CatTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'CatTable 模型加载失败: {e}')

try:
    from . import CatStateModel
    CatStateTable = CatStateModel.CatStateTable
    logger.success('CatStateTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'CatStateTable 模型加载失败: {e}')

try:
    from .import ActionsModel
    ActionsTable = ActionsModel.ActionsTable
    logger.success('ActionsTable 模型加载成功')
except Exception as e:
    print(e)
    logger.error(f'ActionsTable 模型加载失败: {e}')




