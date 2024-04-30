
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
    async def query_info(cls, group_id: str, user_id: str):
        """
        查询游戏信息
        """
        # 获取游戏是否开始
        record = await RouletteGameTable.filter(group_id=group_id, status=1).first()
        if not record:
            return Message('战局尚未开始！')

        current_user_id = record.current_user_id
        at = MessageSegment.at(user_id)
        if user_id != current_user_id:
            return at+Message('当前不是你的回合，请在自己回合查询信息！')

        # 获取游戏玩家
        game_player = await RoulettePlayerTable.get_player(game_id=record.id, uid=user_id)
        card_slot = game_player.card_slot
        msg = at + (
            "\n",
            f"剩余 {game_player.life} 生命\n"
            f"拥有卡片： { ' '.join(game_player.card_slot) if len(card_slot)>0  else '无'}"
        )

        return Message(msg)

    @classmethod
    async def skip(cls, bot: Bot, event: GroupMessageEvent):
        """
        跳过阶段
        """
        group_id = str(event.group_id)
        user_id = str(event.user_id)
        # 获取游戏是否开始
        record = await RouletteGameTable.filter(group_id=group_id, status=1).first()

        if not record:
            return Message(MessageSegment.text('游戏不存在，请先开始战局！'))

        # 如果 用户不再游戏名单，则不做任何操作
        if user_id not in record.player_seat:
            return None

        current_user_id = record.current_user_id
        # 判断是否持枪者回合
        if user_id != current_user_id:
            return Message(at+MessageSegment.text('当前不是你的回合，请等待'))

        state = record.state
        at = MessageSegment.at(user_id)

        if state == 3:
            record.state = 5
            await record.save(update_fields=['state'])
            # 进入下一个流程
            await cls.game_flowing(bot, event)
            return None

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
        # 子弹位置
        current_bullet = record.current_bullet
        # 开始阶段，进行装弹
        if state == 0:
            msg = ''
            print('22222', bullet_count, type(bullet_count))
            if current_bullet != -1:
                # 跳过装弹，抽卡阶段
                record.state = 2
                await record.save(update_fields=['state'])
                await cls.game_flowing(bot, event)
                return
            else:
                msg += 'Oi！子弹都打空了呀～，开始新回合，'

            bullet_list = [random.choice([0, 1]) for _ in range(bullet_count)]
            print('bullet_count', bullet_list)
            msg += f'咔咔咔， {bullet_count}个子弹上膛，天知道有几个空包弹，希望你们能得到幸运鱼的照顾。'
            await asyncio.sleep(1)
            await bot.send(event=event, message=msg)

            # 进入抽卡阶段
            record.state = 1
            record.bullet_list = bullet_list
            record.current_bullet = 0
            await record.save(update_fields=['state', 'bullet_list', 'current_bullet'])
            await cls.game_flowing(bot, event)
            return

        # 开始抽卡
        if state == 1:
            # 开始抽卡
            msg = '开始抽卡，本阶段每人将随机到的两张卡片，如背包已满，则无法获取新卡片\n'

            # 获取游戏玩家
            game_players = await RoulettePlayerTable.get_game_players(record.id)

            cards = ['恢复', '伤害', '预言', '保护', '伪装', '禁锢', '强制']

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

            # 抽卡结束，进入前置buff判定阶段
            record.state = 2
            await record.save(update_fields=['state'])

            await cls.game_flowing(bot, event)
            return

        # 前置buff判定阶段
        if state == 2:
            # 获取持枪者
            current_user_id = record.current_user_id
            player = await RoulettePlayerTable.get_player(game_id=record.id, uid=current_user_id)
            debuff = player.debuff
            at = MessageSegment.at(current_user_id)
            msg = at + ' 你是本轮持枪者，接下来进入你的回合！'
            await asyncio.sleep(1)
            await bot.send(event=event, message=msg)

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
            player = await RoulettePlayerTable.get_player(game_id=record.id, uid=current_user_id)
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
                await bot.send(event=event, message=at + f' 你当前拥有卡片： {" ".join(card_slot)}，是否使用卡片？')
                # 发生提问，流程暂停，等待提问接受

        if state == 5:
            await asyncio.sleep(1)
            at = MessageSegment.at(record.current_user_id)
            msg = at + ' 少年，开枪吧！'
            await bot.send(event=event, message=msg)

        print('流程结束')

    @classmethod
    async def use_card(cls, bot: Bot, event: GroupMessageEvent, card_name: str, at_group: list = [], ):
        """
        使用卡片
        """
        group_id = str(event.group_id)
        user_id = str(event.user_id)

        record = await RouletteGameTable.get_game(group_id)

        if not record:
            return Message(MessageSegment.text('游戏不存在，请先开始战局！'))

        # 如果 用户不再游戏名单，则不做任何操作
        if user_id not in record.player_seat:
            return None

        # 获取持枪者
        current_user_id = record.current_user_id
        # 获取当前回合
        state = record.state
        at = MessageSegment.at(user_id)

        # 判断是否持枪者回合
        if user_id != current_user_id:
            return Message(at+MessageSegment.text('当前不是你的回合，请等待'))

        # 判断当前是否使用卡片回合
        if state != 3:
            return Message(at+MessageSegment.text('当前不是出卡阶段，请重试！'))

        # 获取玩家
        player = await RoulettePlayerTable.get_player(game_id=record.id, uid=user_id)
        card_slot = player.card_slot
        if not card_slot:
            return Message(at+MessageSegment.text('背包为空，无法使用卡片'))

        if card_name not in card_slot:
            return Message(at+MessageSegment.text(f'输入错误或卡片不存在，你当前拥有卡片： {" ".join(card_slot)}'))

        msg = ''
        if card_name == '禁锢' or card_name == '强制':
            # 只能指定一个目标
            if len(at_group) > 1:
                return Message(at+MessageSegment.text('只能指定一个目标'))

            # debuff  来喽
            if len(at_group) == 0:
                # 随机一个目标，添加debuff
                target = random.choice(record.player_seat)
            else:
                target = at_group[0]

            user_player = await RoulettePlayerTable.get_player(record.id, uid=target)
            if not user_player:
                return Message(at+MessageSegment.text('指定目标不存在,请重新选择'))

            user_player.debuff.append(card_name)
            await user_player.save(update_fields=['debuff'])

            msg = '' if len(card_slot) > 0 else ''

            msg = Message(
                at+MessageSegment.text(f'使用卡片「{card_name}」，目标为 ：')+MessageSegment.at(target)+'。')

        # 使用伤害卡片
        if card_name == '伤害':
            # 伤害倍率为2
            player.damage_rate = 2
            await player.save(update_fields=['damage_rate'])

            msg = Message(
                at+MessageSegment.text(f'使用卡片「{card_name}」，下次伤害加倍，如果你打中了的话。'))

        # 使用后置卡片效果
        if card_name == '保护' or card_name == '伪装':

            player.buff.append(card_name)
            await player.save(update_fields=['buff'])

            msg = Message(
                at+MessageSegment.text(f'使用卡片「{card_name}」,请保护好自己！'))

        # 预言卡片
        if card_name == '预言':
            # 子弹位置
            current_bullet = record.current_bullet
            if current_bullet == -1:
                msg = Message(at+MessageSegment.text('已经是最后一颗子弹了，预言失效！'))
            else:
                # 判断下一颗子弹类型
                bullet_type = record.bullet_list[current_bullet]

                bullet_str = '空' if bullet_type == 0 else '实'

                # 创建一个新的列表，长度为6，所有元素都是 '*'
                bullet_display = ['*'] * 6
                for i in range(len(bullet_display)):
                    if i < current_bullet:
                        bullet_display[i] = '空'
                # 如果 current_bullet + 1 位置的子弹类型为空，将这个位置的元素设置为 '空'
                bullet_display[current_bullet] = bullet_str
                # 使用 ' ' 将列表中的元素连接成一个字符串
                bullet_str = ' '.join(bullet_display)

                msg = Message(f'使用了「{card_name}」，你看到枪管内部： {bullet_str}')

        if card_name == '恢复':
            if player.life >= 3:
                msg = Message(
                    at+MessageSegment.text(f'使用了「{card_name}」，但是生命值已满，无法继续恢复！'))
            else:
                player.life += 1
                await player.save(update_fields=['life'])
                msg = Message(
                    at+MessageSegment.text(f'使用了「{card_name}」，生命值+1，当前生命值：{player.life}。'))

        # 从背包中删除对应卡片
        card_slot.remove(card_name)
        player.card_slot = card_slot
        await player.save(update_fields=['card_slot'])

        if len(card_slot) > 0:
            await bot.send(event=event, message=msg+'是否继续使用卡片？')
        else:
            await bot.send(event=event, message=msg)
            record.state = 5
            await record.save(update_fields=['state'])
            # 进入下一个流程
            await cls.game_flowing(bot, event)

        return None

    @classmethod
    async def shoot(cls, bot: Bot, event: GroupMessageEvent, at_group):
        """
        开枪
        """
        group_id = str(event.group_id)
        user_id = str(event.user_id)

        record = await RouletteGameTable.get_game(group_id)

        if not record:
            return Message(MessageSegment.text('游戏不存在，请先开始战局！'))

        # 如果 用户不再游戏名单，则不做任何操作
        if user_id not in record.player_seat:
            return None

        # 获取持枪者
        current_user_id = record.current_user_id
        # 获取当前回合
        state = record.state
        at = MessageSegment.at(user_id)
        # 判断是否持枪者回合
        if user_id != current_user_id:
            return Message(at+MessageSegment.text('当前不是你的回合，请等待'))

        # 判断当前是否使用卡片回合
        if state != 5:
            return Message(at+MessageSegment.text('我不认为现在你该开枪了！'))

        # 当前用户
        player = await RoulettePlayerTable.get_player(game_id=record.id, uid=user_id)

        # 如果不指定目标，则随机
        if len(at_group) == 0:
            # 随机一个目标，添加debuff
            target = random.choice(record.player_seat)
        else:
            target = at_group[0]

        user_at = MessageSegment.at(target)

        if str(target) == str(user_id):
            msg = '你颤颤巍巍的将枪顶住自己的脑门，扣下了扳机！只听 啪一声！'
        else:
            msg = MessageSegment.text('你意气风发的将枪抵在了') + \
                user_at+MessageSegment.text('的脑门，说：再见了朋友！')

        await asyncio.sleep(1)
        await bot.send(event=event, message=msg)

        # buff判定
        # 攻击倍率
        damage_rate = int(player.damage_rate)
        # 攻击目标
        user_player = await RoulettePlayerTable.get_player(game_id=record.id, uid=target)
        # 目标 buff
        buff = user_player.buff
        # 获取子弹当前位置
        current_bullet = record.current_bullet
        # 获取子弹列表
        bullet_list = record.bullet_list

        bullet_type = bullet_list[current_bullet]

        print('bullet_type', bullet_type)

        # 空弹自己
        if bullet_type == 0 and str(target) == str(user_id):
            await bot.send(event=event, message=at+'谢天谢地是空弹，接下来还是我的回合。')
            current_bullet = record.current_bullet
            current_bullet += 1

            if current_bullet > record.bullet_count - 1:
                print('11111', current_bullet, record.bullet_count - 1)
                current_bullet = -1
                record.state = 0

            record.current_bullet = current_bullet
            # 更新数据
            await record.save(update_fields=['current_bullet', 'state'])

            # 进入下一个流程
            await cls.game_flowing(bot, event)
            return None
            
        # 空弹别人
        if bullet_type == 0 and str(target) != str(user_id):
            await bot.send(event=event, message=user_at+'谢天谢地是空弹，接下来持枪者易主。')
            # TODO 这里是改变持枪车的逻辑
            pass
            return None
        

        print(buff)
        # buff 优先级 伤害转移 > 保护
        if '伪装' in buff:
            # 移除当前用户卡片效果
            # user_player.buff.remove('伪装')
            # await user_player.save(update_fields=['buff'])

            target = random.choice(record.player_seat)
            new_player = await RoulettePlayerTable.get_player(game_id=record.id, uid=target)
            new_at = MessageSegment.at(target)
            msg = user_at + \
                MessageSegment.text('使用了伪装，伤害转移给了') + \
                new_at + MessageSegment.text('，他被一枪带走。')

            new_player.life -= damage_rate
            if new_player.life <= 0:
                new_player.life = 0

            # await new_player.save(update_fields=['life'])

            await bot.send(event=event, message=msg)
            # await asyncio.sleep(1)
            # await bot.send(event=event, message=new_at + f'剩余{new_player.life}命')

        return Message(f'攻击倍率：{damage_rate},buff: {buff}')
