
from nonebot_plugin_tortoise_orm import add_model
from ..config import global_config

# 导入插件方法
def set_db_model(model):
    # 获取数据库连接地址
    db_url = global_config.cat_db_url
    # 添加模型
    add_model(model=model, db_name='catdb', db_url=db_url)


# 加载游戏模型
set_db_model(f"{__name__}.CatGameModel")
