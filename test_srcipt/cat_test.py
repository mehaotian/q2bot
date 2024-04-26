from cat import Game

class Record:
    def __init__(self, cleanliness, happiness, sleep, fatigue, hunger):
        # 清洁度
        self.cleanliness = cleanliness
        # 心情
        self.happiness = happiness
        # 睡眠
        self.sleep = sleep
        # 疲劳
        self.fatigue = fatigue
        # 饱食度
        self.hunger = hunger

        # 猫咪的行动状态 0 无事可做 1 睡觉 2 清理 3 喂食 4 玩 5 排泄
        self.action = 0
        # 猫咪年龄
        self.age = 0
        # 猫咪体重
        self.weight = 85

        # 记录猫咪的行动次数，用于计算年龄，常规来说tick一次，半小时过去
        self.age_ticks = 0
        

# 负面属性是 hunger 和 fatigue 
record = Record(cleanliness=100, happiness=100, sleep=100, fatigue=0, hunger=0)
game = Game(record=record)

for i in range(24):
    game.tick()
    print(game.cat)
    game.tick()
    print(game.cat)

