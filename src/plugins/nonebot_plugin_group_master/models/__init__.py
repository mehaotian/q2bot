# 导入插件方法
from nonebot_plugin_tortoise_orm import add_model

#  添加模型
# 添加用户模型
add_model("src.plugins.nonebot_plugin_group_master.models.user_model")
# 添加会话模型
add_model("src.plugins.nonebot_plugin_group_master.models.say_model")
# 添加今日逼王模型
add_model("src.plugins.nonebot_plugin_group_master.models.say_stat_model")