#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   seccurity.py
@Time    :   2024/04/13 00:58:34
@Author  :   haotian 
@Version :   1.0
@Desc    :   密码校验
'''
from typing import Union
from fastapi import Depends,  HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from src.api.core.config import settings


# 获取密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2密码承载
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# 访问令牌过期时间
access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

# 刷新令牌过期时间
refresh_token_expires = timedelta(minutes=settings.REFRESH_ACCESS_TOKEN_EXPIRE_MINUTES)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    创建访问令牌
    参数:
        - data: 数据
        - expires_delta: 过期时间
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt



def get_pwd_hash(password):
    """获取密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_current_username(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户名
    参数:
        - token: 令牌
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username: str = None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

def auth_user(pass1, pass2):
    """
    验证用户
    参数:
        - pass1: 密码1
        - pass2: 密码2
    """

    if not verify_password(pass1, pass2):
        return False
    return True
