#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   responses.py
@Time    :   2023/10/07 16:24:55
@Author  :   haotian
@Version :   1.0
@Desc    :   通用状态码管理
"""
from typing import Any, Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse


# 通用响应模型
class ApiResponse:
    def __init__(
            self,
            ret: int = 0,
            message: str = "Success",
            data: Union[None, Any] = None,
    ):
        self.ret = ret
        self.message = message
        self.data = data


class ApiPageResponse:
    def __init__(
            self,
            ret: int = 0,
            message: str = "Success",
            data: Union[None, Any] = None,
            page: int = 0,
            page_size: int = 0,
            total: int = 0
    ):
        self.ret = ret
        self.message = message
        self.data = data
        self.page = page
        self.page_size = page_size
        self.total = total


# 创建通用响应对象
def create_page_response(ret: int = 0, message: str = "Success", page: int = 0, page_size: int = 0, total: int = 0,
                         data: Any = None):
    return ApiPageResponse(ret=ret, message=message, data=data, page=page, page_size=page_size, total=total)


def create_response(ret: int = 0, message: str = "Success", page: int = 0, page_size: int = 0, total: int = 0,
                    data: Any = None):
    return ApiResponse(ret=ret, message=message, data=data)


# 处理异常并返回通用错误响应
def handle_error_response(e: Exception):
    error_message = "An error occurred."
    status_code = 500

    if isinstance(e, HTTPException):
        error_message = e.detail
        status_code = e.status_code

    return JSONResponse(content=create_response(ret=status_code, message=error_message).dict(), status_code=status_code)
