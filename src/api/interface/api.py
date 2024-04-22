from enum import Enum


class users(Enum):
    """
    定义用户相关接口
    """
    # 接口前缀
    api = "/api/users"
    # 注册用户
    qqauth = f"{api}/qqauth"
    # 登录
    login = f"{api}/login"
    # 忘记密码
    forget_password = f"{api}/forget_password"
    get_user = f"{api}/get_user"


class sys(Enum):
    """
    系统接口
    """
    # 接口前缀
    api = "/api/sys"
    # 提交抽奖
    lottery = f"{api}/lottery"
    # 获取抽奖用户
    get_user = f"{api}/get_user"
    # 验证用户key
    verify_key = f"{api}/verify_key"
