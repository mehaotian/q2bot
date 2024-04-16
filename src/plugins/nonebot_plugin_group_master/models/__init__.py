# 导入插件方法
from nonebot_plugin_tortoise_orm import add_model

# 获取插件的根目录
root = __name__.rpartition('.')[0]
# 添加用户模型
add_model(f"{root}.models.user_model")
# 添加会话模型
add_model(f"{root}.models.say_model")
# 添加今日逼王模型
add_model(f"{root}.models.say_stat_model")
# 添加 steam 数据库
add_model(f"{root}.models.steam_model")
# 添加抽奖模型
add_model(f"{root}.models.reward_model")
# 添加参与抽奖模型
add_model(f"{root}.models.join_lottery_model")
