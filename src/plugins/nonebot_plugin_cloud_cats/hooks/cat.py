import random

class Cat:
    def __init__(self,record):
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
        # # 健康值
        # self.health = record.health

    async def sleep_cat(self):
        """
        睡觉
        """


    async def feed_cat(self):
        """
        喂养猫咪
        """
        pass
    async def play_cat(self):
        """
        逗猫
        """

        pass

    async def clean_cat(self):
        """
        清理猫咪
        """
        pass

    async def is_state(self):
        """
        检查猫咪状态,猫咪同时只能有一个行为
        睡觉  清理  喂食  玩 排泄 无事可做
        优先级为 睡觉>清理>喂食>玩>排泄>无事可做
        """
        sleep = self.sleep
        hunger = self.hunger
        cleanliness = self.cleanliness
        happiness = self.happiness
        fatigue = self.fatigue

        

        

    @classmethod
    async def grow_cat(record):
        """
        猫咪年龄增长
        参数：
            - record: CatTable 猫咪模型
        """
        # 增加年龄
        record.age += 1

        # 根据年龄调整体重
        if record.age < 5:
            record.weight += random.randint(5, 10)
        else:
            record.weight += random.randint(0, 5)

        # 根据年龄调整性格
        if record.age > 3:
            record.character = random.randint(0, 9)

        return await record.save(update_fields=['age', 'weight', 'character'])
    
    def tick(self):
        # 每次 tick 执行时，减少 cleanliness 和 happiness，增加 hunger 和 fatigue
        self.sleep -= 2
        self.cleanliness -= 2
        self.happiness -= 2
        self.hunger += 2
        self.fatigue += 2
    

class Game:
    def __init__(self,record):
        self.cat = Cat(record)

    def tick(self):
        """
        游戏时间流逝
        """
        print(1111)

        