#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   config.py
@Time    :   2023/10/07 16:28:28
@Author  :   haotian
@Version :   1.0
@Desc    :   数据库配置文件
"""

# from pydantic_settings import BaseSettings
from typing import ClassVar
import os


class Settings():
    # 项目名称
    APP_NAME: str = "web 段接口"
    # 是否开启debug
    DEBUG: bool = False
    # 数据库连接URL
    DATABASE_URL: str = "postgres://user:pass@ip/db"

    # 设置为随机的字符串
    SECRET_KEY:str = "91ff62b8c69635ed8338de0199c6da5f7c9b65d1c029daaa1c1cb8c62ff1fa00"
    ALGORITHM:str = "HS256"
    # 访问令牌过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30
    # 过期时间,一个月过期
    REFRESH_ACCESS_TOKEN_EXPIRE_MINUTES:int = 60 * 24 * 30

    # 端口
    PORT: int = 00000
    # 跨域设置
    CORS: ClassVar[dict] = dict(
        allow_origins=[],  # 设置允许的origins来源
        allow_credentials=True,
        # 设置允许跨域的http方法，比如 get、post、put等。
        allow_methods=["*"],
        allow_headers=["*"])  # 允许跨域的headers，可以用来鉴别来源等作用。

    # 程序配置
    BASE_DIR: ClassVar[str] = os.path.dirname(os.path.abspath(__file__))


settings = Settings()
