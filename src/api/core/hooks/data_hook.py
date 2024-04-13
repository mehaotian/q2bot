from src.api.core.utils.security import (
    access_token_expires,
    refresh_token_expires,
    create_access_token,
)


def get_user_data(username):
    """
    获取用户数据
    参数:
        - username: 用户名
    """
    access_token: str = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    refresh_token: str = create_access_token(
        data={"sub": username}, expires_delta=refresh_token_expires
    )
    return {
        "access_token_expires": access_token_expires,
        "refresh_token_expires": refresh_token_expires,
        "refresh_token": refresh_token,
        "access_token": access_token,
        "token_type": "bearer",
    }
