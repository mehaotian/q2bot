

from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
)

from ..models.roulette_game import RouletteGameTable


class GameHook:
    def __init__(self):
        pass

    @classmethod
    async def create_game(cls, group_id: str,player_count:int = 3) -> Message:
        """
        开关游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        record = await RouletteGameTable.get_game(group_id)

        print('record', record)
        if not record:
            # 创建游戏
            roulette =  await RouletteGameTable.create(group_id=group_id,status=0)
            if player_count and player_count >= 2 and player_count <= 5:
                roulette.player_count = player_count 
            else:
                return Message(MessageSegment.text('参与人数最少为2人，最多为5人'))

            await roulette.save(update_fields=['player_count'])
            
            return Message(MessageSegment.text('轮盘赌游戏开始！'))
        else:
           return Message(MessageSegment.text('游戏已经开始，请等待本轮结束！'))

       