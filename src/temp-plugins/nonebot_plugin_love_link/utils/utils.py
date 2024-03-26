import random


def calculate_success_probability(a_charm, b_charm):
    """
    根据魅力值差异计算成功的概率
    :param a_charm: a的魅力值
    :param b_charm: b的魅力值
    :return: 成功的概率（0到1之间的浮点数）
    """
    charm_difference = a_charm - b_charm
    success_rate = 0.0

    if charm_difference <= 0:
        # 概率计算
        probability = a_charm / b_charm

        if probability > 0.1:
            success_rate = 0.7 * probability
        else:
            success_rate = 0.1

    else:
        if b_charm == 0:
            success_rate = 1
        else:
            probability = (charm_difference / b_charm)
            success_rate = 0.3 * probability + 0.7

    return success_rate


def use_item(item_name='', a_charm=0, b_charm=0, item_bonus=0):
    """
    使用提升成功率的道具
    :param item_name: 道具名称
    :param a_charm: a的魅力值
    :param b_charm: b的魅力值
    :return: 是否绑定成功（True/False）
    """
    success_rate = calculate_success_probability(a_charm, b_charm)
    # 计算道具的提升效果，这里假设道具提升了0%的成功率
    print(f'绑定成功概率 {success_rate * 100:.2f}%')

    print(f"使用了道具 {item_name}，绑定成功概率提升 {item_bonus * 100:.2f}%")

    # 应用道具的提升效果
    success_rate += item_bonus

    # 确保成功率在合理范围内
    success_rate = max(success_rate, 0.1)  # 最低成功率为10%
    success_rate = min(success_rate, 1.0)  # 最高成功率为100%

    # 模拟抛硬币来决定成功或失败
    random_number = random.uniform(0, 1)

    if random_number < success_rate:
        return True , success_rate
    else:
        return False , success_rate
