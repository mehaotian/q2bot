import random
import string
import time

def generate_code():
    # 生成一个6位的数字+字母的码
    code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    return code

def store_code(user_id, code):
    # 将这个码和当前时间戳一起存储在数据库中
    timestamp = int(time.time())
    # 这里需要你自己实现将 user_id, code, timestamp 存储到数据库的逻辑

def check_code(user_id, code):
    # 从数据库中获取这个用户的码和时间戳
    # 这里需要你自己实现从数据库中获取数据的逻辑
    # stored_code, timestamp = get_code_from_database(user_id)

    # 检查码是否存在，是否在有效期内，是否已经被使用过
    # if stored_code is None:
    #     return False
    # if stored_code != code:
    #     return False
    # if int(time.time()) - timestamp > 60:
    #     return False

    # # 如果检查通过，将这个码标记为已使用
    # mark_code_as_used(user_id)

    return True

def login(user_id, code):
    # 检查码是否有效
    if not check_code(user_id, code):
        return False

    # 如果有效，允许用户登录
    # 这里需要你自己实现用户登录的逻辑

    return True

def logout(user_id):
    # 用户登出时，生成一个新的码
    code = generate_code()
    store_code(user_id, code)