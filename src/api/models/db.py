#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   db.py
@Time    :   2024/04/13 17:27:03
@Author  :   haotian 
@Version :   1.0
@Desc    :   导出数据库模型
'''


from src.plugins.nonebot_plugin_group_master.models import user_model, say_model

UserTable = user_model.UserTable
SayTable = say_model.SayTable