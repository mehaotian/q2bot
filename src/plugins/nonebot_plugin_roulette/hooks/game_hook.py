
import random
import asyncio

from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
)

from ..models.roulette_game import RouletteGameTable
from ..models.roulette_player import RoulettePlayerTable
from ..models.db import UserTable


class GameHook:
    def __init__(self):
        pass

    @classmethod
    async def create_game(cls, group_id: str, user_id: str, player_count: int = 3) -> Message:
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
            roulette = await RouletteGameTable.create(group_id=group_id, status=0)
            if player_count and player_count >= 2 and player_count <= 5:
                roulette.player_count = player_count
            else:
                return Message(MessageSegment.text('参与人数最少为2人，最多为5人'))

            roulette.user_id = user_id

            await roulette.save(update_fields=['player_count', 'user_id'])

            at = MessageSegment.at(user_id)
            msg = at + ' 开启了一场精彩的轮盘赌，快来参与吧，输入 「/参与战局」 参与游戏。'
            return Message(msg)
        else:
            return Message(MessageSegment.text('游戏已经开始，请等待本轮结束！'))

    @classmethod
    async def close_game(cls, group_id: str, user_id: str) -> Message:
        """
        关闭游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        record = await RouletteGameTable.get_game(group_id, user_id)
        if record:
            uid = record.user_id

            if user_id != uid:
                return Message(MessageSegment.text('只有创建者才能结束游戏'))

            # 关闭游戏
            await RouletteGameTable.close_game(record.id)
            return Message(MessageSegment.text('游戏结束,因为是游戏未结束，所以没有胜者，且不会有任何奖励！'))
        else:
            return Message(MessageSegment.text('游戏不存在,或您非游戏发起者！'))

    @classmethod
    async def join_game(cls, group_id: str, user_id: str) -> Message:
        """
        参与游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        record = await RouletteGameTable.get_game(group_id)
        if record:
            player = await RoulettePlayerTable.get_player(record.id, user_id)
            print('is_player', player)
            if player:
                return Message(MessageSegment.text('您已经参与本场对局，请勿重复加入！'))

            game_players = await RoulettePlayerTable.get_game_players(record.id)

            if game_players and len(game_players) >= record.player_count:
                return Message(MessageSegment.text(f'游戏人数已满，无法继续加入！'))
            # 参与游戏
            player = await RoulettePlayerTable.create_player(group_id, user_id, record.id)

            if not player:
                return Message(MessageSegment.text('参与游戏失败！'))
            msg = MessageSegment.at(
                user_id) + f' 参与了游戏,等待其他玩家参与或等待发起人开始游戏\n本次战局最多支持{record.player_count}人，当前已有{len(game_players)+1}人。'
            return Message(msg)
        else:
            return Message(MessageSegment.text('游戏不存在，请先开始战局！'))

    @classmethod
    async def start_game(cls, group_id: str, user_id: str) -> Message:
        """
        开始游戏
        参数：
            - gid: 群号
            - uid: 用户 ID
        返回：
        """

        # 外面判断了，则必然存在
        record = await RouletteGameTable.get_game(group_id)

        uid = record.user_id
        if user_id != uid:
            return Message(MessageSegment.text('只有战局发起者才能开始游戏'))

        game_players = await RoulettePlayerTable.get_game_players(record.id)
        # 最低两位玩家才能开始游戏
        if game_players and len(game_players) < 2:
            return Message(MessageSegment.text(f'游戏人数不足，无法开始游戏！'))

        # 开始游戏,改变游戏状态
        record.status = 1

        # 随机座位
        seats = []
        print('seats', seats)
        for player in game_players:
            seats.append(player.user_id)

        seats = random.sample(seats, len(seats))

        record.player_seat = seats
        record.current_user_id = seats[0]

        await record.save(update_fields=['status', 'player_seat', 'current_user_id'])
        msg = None
        # 处理游戏开始的消息
        for seat in seats:
            at = MessageSegment.at(seat)
            msg += at + '>'
        # 删除最后的 >
        msg = msg[:-1]
        msg += (
            '\n精彩刺激的轮盘赌开始了哦.\n'
            '系统随机抽取一名玩家作为持枪者，所有玩家注意自己的座位\n'
            '之后游戏将会按照座位顺序进行游戏，祝各位好运！'
        )

        return Message(msg)

    @classmethod
    async def have_game(cls, group_id: str, user_id: str):
        """
        是否存在游戏战局进程
        """
        record = await RouletteGameTable.get_game(group_id)

        if record:
            uid = record.user_id
            if user_id != uid:
                return Message(MessageSegment.text('只有战局发起者才能开始游戏'))

            game_players = await RoulettePlayerTable.get_game_players(record.id)
            # 最低两位玩家才能开始游戏
            if game_players and len(game_players) < 2:
                return Message(MessageSegment.text(f'游戏人数不足，无法开始游戏！'))

            return False
        else:
            return Message(MessageSegment.text('游戏不存在，请先开始战局！'))

    @classmethod
    async def is_nostart_msg(cls, group_id: str, user_id: str):
        """
        是否开始游戏，如果有错误信息，则直接返回
        """
        # 获取游戏是否开始
        record = await RouletteGameTable.filter(group_id=group_id, status=1).first()
        if record:
            uid = record.user_id
            if user_id != uid:
                return Message(MessageSegment.text('你无权开始游戏，只有战局发起者才能开始游戏'))
            return Message(MessageSegment.text('游戏已经开始，请等待本轮结束！'))

        return None
    @classmethod
    async def is_start(cls, group_id: str, user_id: str):
        """
        游戏是否开始
        """
        # 获取游戏是否开始
        record = await RouletteGameTable.filter(group_id=group_id, status=1).first()
        if record:
            return True

        return False

    @classmethod
    async def game_flowing(cls, bot: Bot, event: GroupMessageEvent):
        """
        游戏流程自动判断当前游戏状态
        参数：
            - group_id:
        """
        gid = str(event.group_id)
        # 获取游戏是否开始
        record = await RouletteGameTable.filter(group_id=gid, status=1).first()
        if not record:
            return Message('战局尚未开始！')

        # 行动状态
        state = record.state
        # 子弹数量
        bullet_count = record.bullet_count
        # 开始阶段，进行装弹
        if state == 0:
            bullet_list = [random.choice([0, 1]) for _ in range(bullet_count)]
            print('bullet_count', bullet_list)
            msg = f'卡卡 {bullet_count}个子弹上膛，天知道有几个空包弹，希望你们能得到幸运鱼的照顾。'
            await asyncio.sleep(1)
            await bot.send(event=event, message=msg)

            # 进入抽卡阶段
            record.state = 1
            await record.save(update_fields=['state'])
            await cls.game_flowing(bot, event)
            return

        # 开始抽卡
        if state == 1:
            await asyncio.sleep(1)
            # 开始抽卡
            await bot.send(event=event, message='进入抽卡阶段，本阶段每人将随机到的两张卡片，如背包已满，则无法获取新卡片')

            # 获取游戏玩家
            game_players = await RoulettePlayerTable.get_game_players(record.id)

            cards = ['恢复', '伤害', '预言', '保护', '伪装', '禁锢', '强制']

            msg = None
            for player in game_players:
                card_slot = player.card_slot

                # 计算还可以添加多少张卡片
                num_cards_to_add = min(2, 4 - len(card_slot))

                # 获取at用户
                at = MessageSegment.at(player.user_id)

                if num_cards_to_add > 0:
                    selected_cards = random.sample(cards, num_cards_to_add)
                    player.card_slot.extend(selected_cards)
                    card_slot_str = ' '.join(
                        player.card_slot + ['空'] * (4 - len(player.card_slot)))
                    msg += at + f' 的卡片背包: {card_slot_str}\n'
                    # 保存卡片信息
                    await player.save(update_fields=['card_slot'])
                else:
                    card_slot_str = ' '.join(player.card_slot)
                    msg += at + f' 的卡片背包: {card_slot_str} (满背包，本次抽卡无获得)\n'
            await asyncio.sleep(1)
            await bot.send(event=event, message=Message(msg))
            await asyncio.sleep(1)
            await bot.send(event=event, message='自己回合使用卡片 「 /使用卡片 [卡片名称]」 或者输入 「/pass」 跳过本阶段')

            # 抽卡结束，进入前置buff判定阶段
            record.state = 2
            await record.save(update_fields=['state'])

            await cls.game_flowing(bot, event)
            return
        
        # 前置buff判定阶段
        if state ==2:
            # 获取持枪者
            current_user_id = record.current_user_id
            player = await RoulettePlayerTable.get_player(game_id=record.id,uid=current_user_id)
            debuff = player.debuff
            at = MessageSegment.at(current_user_id)
            msg = at + ' 你是本轮持枪者，接下来进入你的回合！'
            await asyncio.sleep(1)
            await bot.send(event=event,message=msg)

            if not debuff:
                # 无判定直接进入下一个用卡阶段
                record.state = 3
                await record.save(update_fields=['state'])
                await cls.game_flowing(bot, event)
                # msg = at + ' 无负面卡片判定，跳过判定阶段！'
                # return await bot.send(event=event,message=msg)
            else:
                # 有debuff的判定
                pass

        # 用卡阶段
        if state == 3:
            current_user_id = record.current_user_id
            player = await RoulettePlayerTable.get_player(game_id=record.id,uid=current_user_id)
            at = MessageSegment.at(current_user_id)
            card_slot = player.card_slot

            if not card_slot:
                # 无卡牌直接进入下一个用卡阶段
                # await bot.send(event=event, message=at + ' 背包为空，跳过出卡阶段')
                # 直接进入开枪阶段
                record.state = 5
                await record.save(update_fields=['state'])
                await cls.game_flowing(bot, event)
            else:
                await asyncio.sleep(1)
                await bot.send(event=event, message= at + f' 你当前拥有卡片： {" ".join(card_slot)}，是否使用卡片？')
            
            
        print('流程结束')
