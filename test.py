import random

# def calculate_success_probability(a_charm, b_charm):
#     """
#     根据魅力值差异计算成功的概率
#     :param a_charm: a的魅力值
#     :param b_charm: b的魅力值
#     :return: 成功的概率（0到1之间的浮点数）
#     """
#     charm_difference = a_charm - b_charm
#     success_rate = 0.0

#     if charm_difference <= 0:
#         # 概率计算
#         probability = a_charm / b_charm

#         if probability > 0.1:
#             success_rate = 0.7 * probability
#         else:
#             success_rate = 0.1

#     else:
#         probability = ( charm_difference / b_charm )
#         success_rate = 0.3 * probability + 0.7

#     return success_rate

# def use_item(item_name, a_charm, b_charm):
#     """
#     使用提升成功率的道具
#     :param item_name: 道具名称
#     :param a_charm: a的魅力值
#     :param b_charm: b的魅力值
#     :return: 是否绑定成功（True/False）
#     """
#     success_rate = calculate_success_probability(a_charm, b_charm)

#     print(f'绑定成功概率 {success_rate * 100:.2f}%')
#     # 计算道具的提升效果，这里假设道具提升了0%的成功率
#     item_bonus = 0

#     print(f"使用了道具 {item_name}，绑定成功概率提升 {item_bonus * 100:.2f}%")

#     # 应用道具的提升效果
#     success_rate += item_bonus

#     # 确保成功率在合理范围内
#     success_rate = max(success_rate, 0.1)  # 最低成功率为10%
#     success_rate = min(success_rate, 1.0)  # 最高成功率为100%

#     # 模拟抛硬币来决定成功或失败
#     random_number = random.uniform(0, 1)
#     if random_number < success_rate:
#         return True
#     else:
#         return False

# # 示例用法
# a_charm = 210  # 请根据实际情况设置a和b的魅力值
# b_charm = 100
# item_name = "魅力护符"
# success = use_item(item_name, a_charm, b_charm)

# if success:
#     print("绑定成功！")
# else:
#     print("绑定失败，请提高魅力值或使用道具。")
# user_list = ['大鹅', '老虚', '城管']
# join_number = 3
# participants = user_list[:join_number]

# # 创建一个列表，包含所有参与者
# lottery_pool = list(participants)


# # 执行一百次 ，并统计 每个人中奖的次数
# def choice(count = 100):
#     result = {}
#     for i in range(count):
#         # 随机选择一个参与者
#         winner = random.choice(lottery_pool)
#         # 将中奖者加入结果字典，并记录中奖次数
#         if winner in result:
#             result[winner] += 1
#         else:
#             result[winner] = 1

#     return result


# print('第一次随机 100 次',choice())
# print('第二次随机 1000 次',choice(1000))
# print('第三次随机 10000 次',choice(10000))
# print('第四次随机 100000 次',choice(100000))
# print('第五次随机 1000000 次',choice(1000000))

# 初始化一个字典来记录每个数字出现的次数
count_dict = {i: 0 for i in range(1, 101)}

# 随机生成 100 次 1 到 100 之间的数字，并记录每个数字出现的次数
for _ in range(100):
    num = random.randint(1, 100)
    count_dict[num] += 1

# 打印每个数字出现的次数
for num, count in count_dict.items():
    if count > 0:
        print(f"数字 {num} 出现了 {count} 次")