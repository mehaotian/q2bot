import random

# class Player:
#     def __init__(self, level=1, current_exp=0):
#         self.level = level
#         self.current_exp = current_exp
    
#     def total_exp_for_level(self, level: int):
#         """
#         计算达到某等级所需的总经验
#         参数：
#           - level: 等级
#         返回：
#           - 达到该等级所需的总经验
#         """
#         base_exp = 100  # 初始等级所需经验
#         growth_rate = 1.1  # 每级递增系数
#         total_exp = 0

#         for lvl in range(1, level + 1):
#             exp_for_current_level = base_exp * (growth_rate ** (lvl - 1))
#             total_exp += int(exp_for_current_level)

#         return total_exp

#     def exp_to_next_level(self):
#         """
#         计算到下一级所需的经验
#         返回：
#           - 当前等级进度（当前经验/到下一级经验）
#           - 升级还需多少经验
#         """
#         current_level_exp = self.total_exp_for_level(self.level)  # 当前等级所需总经验
#         next_level_exp = self.total_exp_for_level(self.level + 1)  # 下一等级所需总经验
#         exp_for_next_level = next_level_exp - current_level_exp  # 到下一级所需经验

#         return exp_for_next_level


# # 循环输入每级的所需要的经验
# for lv in range(100):
#     lv += 1
#     player = Player(level=lv)
#     total_exp = player.total_exp_for_level(lv)
#     next_exp = player.exp_to_next_level()
#     print(f"等级 {lv}，下一级: {total_exp} , 升级还需：{next_exp}")
def calculate_attribute_balance(level, base_stat=10):
    """
    根据只因的等级计算各属性的平衡分配。
    
    参数:
    - level: 当前只因的等级
    - base_stat: 基础属性值
    
    返回:
    - 各属性的数值字典
    """
    # 定义一个属性分配比例的基础值
    total_points = level * 10  # 每级10点属性分配
    attributes = {
        'z_attack': base_stat,
        'z_defense': base_stat,
        'z_speed': base_stat,
        'z_crit': base_stat,
        'z_hit': base_stat,
        'z_dodge': base_stat,
        'z_skill': base_stat,
        'z_equipment': base_stat,
    }
    
    # 分配剩余属性点
    remaining_points = total_points
    while remaining_points > 0:
        attr = random.choice(list(attributes.keys()))
        add_points = random.randint(1, min(3, remaining_points))  # 每次分配1-3点
        attributes[attr] += add_points
        remaining_points -= add_points

    # 属性间基本平衡调整 (攻击、命中稍微重要一些)
    attributes['z_attack'] += 0.2 * level
    attributes['z_hit'] += 0.15 * level
    attributes['z_speed'] += 0.1 * level
    attributes['z_defense'] += 0.1 * level
    attributes['z_crit'] += 0.05 * level
    attributes['z_dodge'] += 0.05 * level
    
    return attributes


print(calculate_attribute_balance(10))