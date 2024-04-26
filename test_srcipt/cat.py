import random

# min(100, max(0, self.hunger + random.randint(1, 2)))


def calc_attr(value, minval=1, maxval=3, type='up',mins=0,maxs=100):
    """
    计算属性值，默认增加 1-3 点，限制在 0-100 之间
    """
    if type == 'up':
        return min(maxs, max(mins, value + random.randint(minval, maxval)))
    else:
        return min(maxs, max(mins, value - random.randint(minval, maxval)))


class Cat:
    def __init__(self, record):
        # 饥饿值
        self.hunger = record.hunger
        # 清洁值
        self.cleanliness = record.cleanliness
        # 快乐值
        self.happiness = record.happiness
        # 疲劳值
        self.fatigue = record.fatigue
        # 睡眠值
        self.sleep = record.sleep

        # 猫咪年龄
        self.age = record.age
        # 猫咪体重
        self.weight = record.weight

        # 记录猫咪的行动次数，用于计算年龄，常规来说tick一次，半小时过去
        self.age_ticks = record.age_ticks

        # 行动
        self.action = record.action
        # # 健康值
        # self.health = record.health

        # 临时行动，用于记录上一个行动
        self.temp_action = 0

    def sleep_cat(self):
        """
        猫咪睡觉：
            睡眠 +(10-20)
            疲劳 -(10-20)
            心情 -(2-5)
            饥饿 +(2-4)
            不影响清洁度
        醒来：
            睡眠值达到 100 并且疲劳值低于 30 时，猫咪会自动醒来,并重置状态
            饥饿 >= 90 时，猫咪会自动醒来,并开始进食

        影响：
            睡眠状态下，猫咪个属性都会有所变化，处于持续增加的状态
            猫咪需要睡觉来自我调整
            但是长时间的睡眠，会导致心情变差，因为缺少了活动
        """
        # 睡眠值增加
        self.sleep = calc_attr(self.sleep, 10, 20)
        # 疲劳值减少
        self.fatigue = calc_attr(self.fatigue, 10, 20, 'down')
        # 心情变差
        self.happiness = calc_attr(self.happiness, 2, 5,'down')
        # 饥饿增加
        self.hunger = calc_attr(self.hunger, 2, 5)

        sleep = self.sleep
        fatigue = self.fatigue

        # 退出睡眠状态
        if sleep >= 100 and fatigue < 30:
            self.change_state()

        # 如果过于饥饿，猫咪会起来进食
        if self.hunger >= 90:
            self.action = 3
            self.temp_action = 3
            self.feed_cat()

    def feed_cat(self):
        """
        猫咪进食：
            饥饿 0 ，吃一次就饱了，（假设有食物，如果没有食物，饥饿值不变）
            心情 + (10-20)
            疲劳 + (20-30)
            睡眠 - (20-30)
            不影响清洁度
        影响：
            进食状态下，猫咪会在一个回合内吃饱，饥饿值会直接变为 0
            猫咪进食后，会增加心情，但是会增加疲劳，因为吃饱了就想睡觉
            但是长时间的睡眠，会导致心情变差，因为缺少了活动
        """
        self.hunger = 0
        self.happiness = calc_attr(value=self.happiness, minval= 10, maxval=20,maxs=80)
        self.fatigue = calc_attr(self.fatigue, 20, 30)
        self.sleep = calc_attr(self.sleep, 20, 30, 'down')

        self.change_state()

    def play_cat(self):
        """
        猫咪自己玩：
            + 心情 10-20
            + 疲劳 5-18
            - 睡眠 5-18
            + 饥饿 5-15
            - 清洁 5-15
        玩耍完毕：
            心情达到 80 时，猫咪会自动停止玩耍，并重置状态
            疲劳 > 70 或者睡眠 < 30 时，猫咪会自动停止玩耍，并开始入睡
            饥饿 >70 时，猫咪会自动停止玩耍，并开始进食
            清洁 < 30 时，猫咪会自动停止玩耍，并开始清理

        如果 健康值小于 40 的时候，猫咪拒绝玩耍
        影响：
            玩耍状态下，猫咪的心情会增加，但是会增加疲劳，因为玩耍会消耗体力
            玩耍后，会增加饥饿度，因为玩耍会消耗体力
            玩耍后，会减少清洁度，因为玩耍会弄脏自己
        """
        health = self.health
        if health < 40:
            print('猫咪拒绝玩耍')
            self.action = 1
            self.temp_action = 1
            self.sleep_cat()
            return

        self.happiness = calc_attr(value=self.happiness, minval= 10, maxval=20,maxs=80)
        self.fatigue = calc_attr(self.fatigue, 5, 18)
        self.sleep = calc_attr(self.sleep, 5, 18, 'down')
        self.hunger = calc_attr(self.hunger, 5, 10)
        self.cleanliness = calc_attr(self.cleanliness, 8, 15, 'down')

        happiness = self.happiness
        fatigue = self.fatigue
        sleep = self.sleep
        hunger = self.hunger
        cleanliness = self.cleanliness

        # 退出玩耍状态
        if happiness >= 80:
            self.change_state()

        if fatigue > 70 or sleep < 30:
            self.action = 1
            self.temp_action = 1
            self.sleep_cat()

        if hunger > 70:
            self.action = 3
            self.temp_action = 3
            self.feed_cat()

        if cleanliness < 30:
            self.action = 2
            self.temp_action = 2
            self.clean_cat()

    def clean_cat(self):
        """
        猫咪清理：
            + 清洁 20-40
            - 心情 2-4
            - 疲劳 2-4
            - 睡眠 2-4
            + 饥饿 5-8
            不影响饥饿度
        清理完毕
            清洁值达到 80 时，猫咪会自动停止清理,并重置状态
            疲劳 > 70 或者睡眠 < 30 时，猫咪会自动停止玩耍，并开始入睡
            饥饿 >70 时，猫咪会自动停止玩耍，并开始进食

        影响：
            清理状态下，猫咪的清洁度会增加，但是会减少心情，因为清洁会让猫咪感到不舒服
            清理后，会减少疲劳，因为清理会让猫咪感到放松
            清理后，会减少睡眠，因为清理会让猫咪感到兴奋
            清理后，会增加饥饿度，因为清理会消耗体力

        """
        self.cleanliness = calc_attr(value=self.cleanliness, minval= 20, maxval=40,maxs=80)
        self.happiness = calc_attr(value=self.happiness, minval= 10, maxval=20,maxs=80)
        self.fatigue = calc_attr(self.fatigue, 2, 4, 'down')
        self.sleep = calc_attr(self.sleep, 2, 4, 'down')
        self.hunger = calc_attr(self.hunger, 5, 8)

        cleanliness = self.cleanliness
        fatigue = self.fatigue
        sleep = self.sleep
        hunger = self.hunger

        # 退出清理状态, 猫咪的清洁值最多到80 ，必须洗澡才能达到100
        if cleanliness >= 80:
            self.change_state()

        if fatigue > 70 or sleep < 30:
            self.action = 1
            self.temp_action = 1
            self.sleep_cat()

        if hunger > 70:
            self.action = 3
            self.temp_action = 3
            self.feed_cat()

    def grow_cat(self):
        """
        猫咪年龄增长
        """
        # 根据年龄调整体重
        if self.age < 5:
            self.weight += random.randint(5, 10)
        else:
            self.weight += random.randint(0, 5)

        # # 根据年龄调整性格
        # if record.age > 3:
        #     record.character = random.randint(0, 9)

        # return await record.save(update_fields=['age', 'weight', 'character'])

    @property
    def health(self):
        """
        获取猫咪健康值
        """
        return self.calculate_health()
    def calculate_health(self):
        hunger = self.hunger
        cleanliness = self.cleanliness 
        happiness = self.happiness 
        fatigue = self.fatigue 
        sleep = self.sleep

        # 定义每个属性的权重
        weights = {'hunger': 0.1, 'cleanliness': 0.1,
                   'happiness': 0.3, 'fatigue': 0.1, 'sleep': 0.3}

        # 计算健康值
        health = (weights['hunger'] * (1 - hunger / 100) +
                  weights['cleanliness'] * (cleanliness / 100) +
                  weights['happiness'] * (happiness / 100) +
                  weights['fatigue'] * (1 - fatigue / 100) +
                  weights['sleep'] * (sleep / 100))

        return int(health * 100)  # 将健康值转换为0到100的范围
    # 状态变化

    def change_state(self):
        # 判断猫咪状态，每次猫咪只有一个行动，优先级为 睡眠>进食>清理>排泄>玩耍
        # 睡觉
        if self.sleep <= 50 or self.fatigue >= 50:
            self.action = 1
        elif self.hunger >= 50:
            self.action = 3
        elif self.cleanliness <= 50:
            self.action = 2
        elif self.happiness <= 50:
            self.action = 4
        else:
            self.action = 0

    def tick(self):
        # 每次 tick 执行时，减少 cleanliness 和 happiness，增加 hunger 和 fatigue
        # 随机增加 2-5点属性
        self.sleep = calc_attr(self.sleep, 5, 10, 'down')
        self.cleanliness = calc_attr(self.cleanliness, 2, 5, 'down')
        self.happiness = calc_attr(self.happiness, 8, 10, 'down')
        self.hunger = calc_attr(self.hunger, 4, 8)
        self.fatigue = calc_attr(self.fatigue, 2, 5)

        # 检测喵咪状态
        self.change_state()
    
    def _health_str(self):
        health = self.calculate_health()
        if health >= 80:
            return '健康'
        elif health >= 40:
            return '亚健康'
        elif health >= 20:
            return '不健康'
        else:
            return '濒死'

    def __str__(self) -> str:
        actions = {
            0: '无事',
            1: '睡觉',
            2: '清理',
            3: '吃饭',
            4: '玩耍',
            5: '排泄'
        }

        return (
            f'Cat: '
            f'年龄={self.age:<3}, '
            f'饥饿={self.hunger:<3}, '
            f'清洁={self.cleanliness:<3}, '
            f'心情={self.happiness:<3}, '
            f'疲劳={self.fatigue:<3}, '
            f'睡眠={self.sleep:<3}, '
            f'健康={self._health_str():<3},'
            f'行动={actions[self.temp_action]:<8} '
        )


class Game:
    def __init__(self, record):
        self.cat = Cat(record)

    def tick(self):
        """
        游戏时间流逝
        """
        self.cat.age_ticks += 1
        self.cat_age()
        
        action = self.cat.action
        self.cat.temp_action = action
        # 如果猫咪无事正常 tick
        if action == 0:
            self.cat.tick()

        # 睡觉
        elif action == 1:
            self.cat.sleep_cat()
        # 清理
        elif action == 3:
            self.cat.feed_cat()
        # 喂食
        elif action == 4:
            self.cat.play_cat()
        # 玩耍
        elif action == 2:
            self.cat.clean_cat()

    def cat_age(self):
        """
        猫咪年龄增长
        """

        if self.cat.age_ticks >= 336:
            self.cat.age += 1
            self.cat.age_ticks = 0

        self.cat.grow_cat()
