
from nonebot import require
from datetime import date, datetime, timedelta
import random
import asyncio
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
    ActionFailed,
)
from nonebot.log import logger
from ..models.roulette_game import RouletteGameTable
from ..models.roulette_player import RoulettePlayerTable
from ..models.db import UserTable
from ..config import global_config
from ..text2img.txt2img import txt2img
from ..text2img.user2img import user_2_img

# 获取超级管理员
su = global_config.superusers
print('global_config', global_config)
GAME_RESPONSE_TIME = global_config.game_response_time
PLAYER_RESPONSE_TIME = global_config.player_response_time

# 定时任务
try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None


class GameHook:
    def __init__(self):
        pass

    @classmethod
    async def get_info(cls,user_id: str, group_id: str):
        """
        获取用户信息
        """
        sender_user = await UserTable.get_user(user_id=user_id, group_id=group_id)
        print('user', dict(sender_user))
        
        last_sign = await UserTable.get_last_sign(user_id, group_id)
        # 判断是否已签到
        today = date.today()
        logger.debug(f"last_sign: {last_sign}")
        logger.debug(f"today: {today}")

        bg_img = sender_user.bg_img or ''
        # 是否签到
        is_sign = today == last_sign
        is_ok, sign_img_file = user_2_img(
            nickname=sender_user.nickname,
            bg_path=bg_img,
            user_id=user_id,
            group_id=group_id,
            data=dict(sender_user),
            is_sign=is_sign
        )
        if is_ok:
            msg =MessageSegment.at(user_id = user_id) + MessageSegment.image(file=sign_img_file)
            return msg
        else:
            msg_txt = MessageSegment.at(user_id = user_id)
            msg_txt += f"当前金币：{sender_user.gold}\n"
            msg_txt += f"是否签到：{'已签到' if is_sign else '未签到'}\n"

            return Message(msg_txt)


    @classmethod
    async def create_game(cls, group_id: str, user_id: str, player_count: int = 5) -> Message:
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
                return Message(MessageSegment.text('喵叽提醒：参与人数最少为2人，最多为5人哦'))

            roulette.user_id = user_id

            await roulette.save(update_fields=['player_count', 'user_id'])

            at = MessageSegment.at(user_id)
            msg = at + ' 和喵叽酱一起轮盘赌叭，输了嘻嘻嘻~（坏心思），输入 「/参与战局」 参与游戏！'

            # 添加游戏定时任务，需要10分钟后无响应关闭
            cls.set_scheduler(type=1, user_id=user_id, group_id=group_id)
            return Message(msg)
        else:
            return Message(MessageSegment.text('游戏已经开始，请等待本轮结束！'))

    @classmethod
    async def close_game(cls, group_id: str, user_id: str, auto_end: bool = False) -> Message:
        """
        关闭游戏
        参数：
            - gid: 群号
        返回：
            - Message
        """
        # 获取游戏是否存在
        record = await RouletteGameTable.get_game(group_id)
        if record:
            uid = record.user_id

            if user_id != uid and user_id not in su:
                return Message(MessageSegment.text('只有创建者才能结束游戏'))

            # 关闭游戏
            await RouletteGameTable.close_game(record.id)
            if auto_end:
                return Message('喵叽提醒：因长时间未开始，游戏已自动关闭！')

            # 关闭定时任务
            # 任务id
            task_id = f"{group_id}_1"
            # 玩家任务id
            task_play_id = f"{group_id}_2"
            # 手动停止任务
            cls.end_scheduler(task_id)
            cls.end_scheduler(task_play_id)

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
            at = MessageSegment.at(user_id)
            print('is_player', player)
            if player:
                return Message(at+MessageSegment.text(' 喵叽提醒：身在局中，请勿重复加入！'))

            game_players = await RoulettePlayerTable.get_game_players(record.id)

            if game_players and len(game_players) >= record.player_count:
                return Message(at+MessageSegment.text(f' 喵叽提醒：满了满了，下次在进来好吗？'))
            # 参与游戏
            player = await RoulettePlayerTable.create_player(group_id, user_id, record.id)

            if not player:
                return Message(at+MessageSegment.text(' 参与游戏失败！'))
            msg = at + \
                f' （囚笼）可爱的喵叽酱俘虏了你，变为棋子叭~烧年~\n战局最多{record.player_count}人，当前已有{len(game_players)+1}人。'

            # 更新游戏定时任务
            cls.set_scheduler(type=1, user_id=user_id, group_id=group_id)
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
        at = MessageSegment.at(user_id)
        uid = record.user_id
        if user_id != uid:
            return Message(at+MessageSegment.text(' 喵叽提醒：只有游戏发起者才能开始游戏嗷~'))

        game_players = await RoulettePlayerTable.get_game_players(record.id)
        # 最低两位玩家才能开始游戏
        if not game_players or len(game_players) < 2:
            return Message(at+MessageSegment.text(f' 喵叽提醒：游戏人数不足，无法开始游戏嗷 ~'))

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
            '\n喵叽酱关上了笼子。\n'
            '喵叽酱将会为各位小少年安排专属座位。\n'
            '乖乖宝宝都是听话的嗷~ 一会按座位行动才行呢。\n'
            '看看是谁会获得喵叽酱的宠幸呢~? 祝各位好运！'
        )

        # 更新游戏响应时间
        cls.set_scheduler(type=1, user_id=user_id, group_id=group_id)

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
                return Message(MessageSegment.text('无权限'))

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
                return Message(MessageSegment.text(' 喵叽提醒：你无权开始游戏，只有战局发起者才能开始游戏'))
            return Message(MessageSegment.text(' 喵叽提醒：游戏已经开始，请等待本轮结束！'))

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
            f"拥有卡片： { ' '.join(game_player.card_slot) if len(card_slot)>0  else '无'}\n"
        )
        buff = game_player.buff
        buff = ' '.join(buff) if len(buff) > 0 else '无'
        debuff = game_player.debuff
        debuff = ' '.join(debuff) if len(debuff) > 0 else '无'
        # 伤害倍率
        damage_rate = game_player.damage_rate
        msg += (
            f"伤害倍率： {damage_rate}倍\n"
            f"增益效果： {buff}\n"
            f"负面效果： {debuff}\n"
        )

        # 更新游戏响应时间
        cls.set_scheduler(type=1, user_id=user_id, group_id=group_id)

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
            return Message(MessageSegment.text(' 喵叽提醒：游戏不存在，请先开始战局！'))

        # 如果 用户不再游戏名单，则不做任何操作
        if user_id not in record.player_seat:
            return None

        current_user_id = record.current_user_id
        # 判断是否持枪者回合
        if user_id != current_user_id:
            return Message(at+MessageSegment.text(' 喵叽提醒：当前不是你的回合，请等待'))

        state = record.state
        at = MessageSegment.at(user_id)

        if state == 3:
            record.state = 5
            await record.save(update_fields=['state'])
            # 进入下一个流程
            await cls.game_flowing(bot, event)
            return None

    @classmethod
    async def game_flowing(cls, bot: Bot = None, event: GroupMessageEvent = None, user_id: str = '', group_id: str = ''):
        """
        游戏流程自动判断当前游戏状态
        参数：
            - group_id:
        """
        if not user_id:
            uid = str(event.user_id)
        else:
            uid = user_id
        if not group_id:
            gid = str(event.group_id)
        else:
            gid = group_id

        if not bot:
            bots = get_bot()

        # 获取游戏是否开始
        record = await RouletteGameTable.filter(group_id=gid, status=1).first()
        if not record:
            return Message('喵叽提醒：游戏尚未开始嗷~')

        # 判断胜利
        player_seat = record.player_seat

        # 只要进入流程就更新
        # 更新游戏响应时间
        cls.set_scheduler(type=1, user_id=uid, group_id=gid)
        # 更新玩家响应时间
        cls.set_scheduler(type=2, user_id=record.current_user_id, group_id=gid)

        if len(player_seat) == 1:
            winner_id = player_seat[0]
            at = MessageSegment.at(winner_id)
            msg = '让我们恭喜' + at + '获得最后的胜利！呱唧呱唧！'
            if not bot:
                await bots.send_group_msg(group_id=gid, message=msg)
            else:
                await bot.send(event=event, message=msg)

            player = await RoulettePlayerTable.get_player(game_id=record.id, uid=winner_id)
            player.status = 1

            await player.save(update_fields=['status'])
            record.winner_id = winner_id
            record.status = 2

            await record.save(update_fields=['winner_id', 'status'])
            if not bot:
                await bots.send_group_msg(group_id=gid, message='本轮游戏结束！请等待结算~')
            else:
                await bot.send(event, '本轮游戏结束！请等待结算~')
            players = await RoulettePlayerTable.filter(game_id=record.id).all()
            # 败方金币总额
            total_lose = 0
            lose_msg = ''
            for player in players:
                user = await UserTable.get_user(user_id=player.user_id, group_id=player.group_id)
                if player.status == 2:
                    chips = player.chips
                    if user.gold < chips:
                        chips = user.gold
                    total_lose += chips
                    user.gold -= player.chips
                    if user.gold < 0:
                        user.gold = 0
                    await user.save(update_fields=['gold'])
                    lose_msg += f'"{user.nickname}" 输掉了 {player.chips} 金币，剩余 {user.gold} 金币\n'

            player_winner = next(
                (player for player in players if player.status == 1), None)

            if player_winner:
                user = await UserTable.get_user(user_id=player_winner.user_id, group_id=player_winner.group_id)
                user.gold += total_lose
                await user.save(update_fields=['gold'])
                msg = f'"{user.nickname}" 是最后的胜利者，赢得了 {total_lose} 金币，共有 {user.gold} 金币\n' + lose_msg
                if not bot:
                    await bots.send_group_msg(group_id=gid, message=msg)
                else:
                    await bot.send(event, msg)

            # 手动停止任务
            # 任务id
            task_id = f"{gid}_1"
            # 玩家任务id
            task_play_id = f"{gid}_2"
            cls.end_scheduler(task_id)
            cls.end_scheduler(task_play_id)

            return

        # 行动状态
        state = record.state
        # 子弹数量
        bullet_count = record.bullet_count
        # 子弹位置
        current_bullet = record.current_bullet
        # 开始阶段，进行装弹
        if state == 0:
            msg = ''
            if len(record.bullet_list) > 0:
                if current_bullet != -1:
                    # 跳过装弹，抽卡阶段
                    record.state = 2
                    await record.save(update_fields=['state'])
                    if not bot:
                        await cls.game_flowing(user_id=uid, group_id=gid)
                    else:
                        await cls.game_flowing(bot, event)
                    return
                else:
                    msg += 'Oi！子弹都打空了呀～，喵叽酱帮你们重新装蛋吧！\n'

            bullet_list = [random.choice([0, 1]) for _ in range(bullet_count)]
            print('bullet_count', bullet_list)
            # msg += f'咔咔咔， {bullet_count}个子弹上膛，天知道有几个空包弹，希望你们能得到幸运鱼的照顾。'
            msg += f'愚蠢的小手枪有{bullet_count}个房间，调皮的喵叽酱打翻了几个原住民~天知道还有几个在家，各位小心喽~'
            await asyncio.sleep(1)
            if not bot:
                await bots.send_group_msg(group_id=gid, message=msg)
            else:
                await bot.send(event=event, message=msg)

            # 进入抽卡阶段
            record.state = 1
            record.bullet_list = bullet_list
            record.current_bullet = 0
            await record.save(update_fields=['state', 'bullet_list', 'current_bullet'])
            if not bot:
                await cls.game_flowing(user_id=uid, group_id=gid)
            else:
                await cls.game_flowing(bot, event)
            return

        # 开始抽卡
        if state == 1:
            # 开始抽卡
            # msg = '开始抽卡，本阶段每人将随机到的两张卡片，如背包已满，则无法获取新卡片\n'
            msg = '喵叽酱给每人两张卡片，如果你装不下，那就丢掉了嗷~ 做人不要贪得无厌嘛~\n'

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
                    msg += at + f' 卡包: 「{card_slot_str}」\n'
                    # 保存卡片信息
                    await player.save(update_fields=['card_slot'])
                else:
                    card_slot_str = ' '.join(player.card_slot)
                    msg += at + f' 的卡包: 「{card_slot_str}」 (已满，无获得)\n'
            await asyncio.sleep(1)
            if not bot:
                await bots.send_group_msg(group_id=gid, message=msg)
            else:
                await bot.send(event=event, message=Message(msg))

            # 抽卡结束，进入前置buff判定阶段
            record.state = 2
            await record.save(update_fields=['state'])

            if not bot:
                await cls.game_flowing(user_id=uid, group_id=gid)
            else:
                await cls.game_flowing(bot, event)
            return

        # 前置buff判定阶段
        if state == 2:
            # 获取持枪者
            current_user_id = record.current_user_id
            player = await RoulettePlayerTable.get_player(game_id=record.id, uid=current_user_id)
            debuff = player.debuff
            at = MessageSegment.at(current_user_id)
            msg = at + ' 到你开枪喽~让我看看倒霉蛋在哪里~'
            await asyncio.sleep(1)
            if not bot:
                await bots.send_group_msg(group_id=gid, message=msg)
            else:
                await bot.send(event=event, message=msg)

            if not debuff:
                # 无判定直接进入下一个用卡阶段
                record.state = 3
                await record.save(update_fields=['state'])
                if not bot:
                    await cls.game_flowing(user_id=uid, group_id=gid)
                else:
                    await cls.game_flowing(bot, event)
                return

            else:
                # 有debuff的判定
                print('debuff', debuff)
                if "禁锢" in debuff:
                    # 禁锢，直接跳过用卡阶段
                    player.debuff.remove('禁锢')
                    await player.save(update_fields=['debuff'])
                    player_seat = record.player_seat[:]
                    # 获取下一个人
                    next_current_id = cls.get_next_id(
                        player_seat, record.current_user_id)
                    # 换人
                    record.current_user_id = next_current_id
                    record.state = 0

                    await record.save(update_fields=['state', 'current_user_id'])
                    if not bot:
                        await bots.send_group_msg(group_id=gid, message=at+'【禁锢】生效，本轮你无法行动！')
                    else:
                        await bot.send(event=event, message=at+'【禁锢】生效，本轮你无法行动！')
                    if not bot:
                        await cls.game_flowing(user_id=uid, group_id=gid)
                    else:
                        await cls.game_flowing(bot, event)
                    return

                if '强制' in debuff:
                    # 预留到开枪的时候使用
                    record.state = 3
                    await record.save(update_fields=['state'])
                    if not bot:
                        await bots.send_group_msg(group_id=gid, message=msg)
                    else:
                        await bot.send(event=event, message=at+'【强制】生效，接下来你只能攻击自己嗷~')

                    if not bot:
                        await cls.game_flowing(user_id=uid, group_id=gid)
                    else:
                        await cls.game_flowing(bot, event)
                    return

        # 用卡阶段
        if state == 3:
            current_user_id = record.current_user_id
            player = await RoulettePlayerTable.get_player(game_id=record.id, uid=current_user_id)
            at = MessageSegment.at(current_user_id)
            card_slot = player.card_slot

            if not card_slot:
                # 无卡牌直接进入下一个用卡阶段
                # 直接进入开枪阶段
                record.state = 5
                await record.save(update_fields=['state'])
                if not bot:
                    await cls.game_flowing(user_id=uid, group_id=gid)
                else:
                    await cls.game_flowing(bot, event)
            else:
                await asyncio.sleep(1)
                msg = at + f' 你的卡包：「{" ".join(card_slot)}」，是否使用卡片？'
                if not bot:
                    await bots.send_group_msg(group_id=gid, message=msg)
                else:
                    await bot.send(event=event, message=msg)
                # 发生提问，流程暂停，等待提问接受

        if state == 5:
            await asyncio.sleep(1)
            at = MessageSegment.at(record.current_user_id)
            msg = at + ' 小骚年，举起你的大枪，让我看看你的实力~'
            if not bot:
                await bots.send_group_msg(group_id=gid, message=msg)
            else:
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
            return Message(MessageSegment.text(' 喵叽提醒：游戏不存在，请先开始战局！'))

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
            return Message(at+MessageSegment.text(' 喵叽提醒：当前不是你的回合嗷~请等待！'))

        # 更新玩家响应时间
        cls.set_scheduler(type=2, user_id=current_user_id, group_id=group_id)
        cls.set_scheduler(type=1, user_id=current_user_id, group_id=group_id)

        # 判断当前是否使用卡片回合
        if state != 3:
            return Message(at+MessageSegment.text('  喵叽提醒：当前不是出卡阶段嗷~请重试！'))

        # 获取玩家
        player = await RoulettePlayerTable.get_player(game_id=record.id, uid=user_id)
        card_slot = player.card_slot
        if not card_slot:
            return Message(at+MessageSegment.text(' 喵叽提醒：卡包为空，无法使用卡片'))

        if card_name not in card_slot:
            return Message(at+MessageSegment.text(f'  喵叽提醒：输入错误或卡片不存在，你当前拥有卡片： 【{" ".join(card_slot)}】'))

        msg = ''
        if card_name == '禁锢' or card_name == '强制':
            # 只能指定一个目标
            if len(at_group) > 1:
                return Message(at+MessageSegment.text(' 喵叽提醒：只能指定一个目标嗷~'))

            # debuff  来喽
            if len(at_group) == 0:
                # 随机一个目标，添加debuff
                target = random.choice(record.player_seat)
            else:
                target = at_group[0]

            user_player = await RoulettePlayerTable.get_player(record.id, uid=target)
            if not user_player:
                return Message(at+MessageSegment.text('  喵叽提醒：指定目标不存在,请选一个吧！'))

            user_player.debuff.append(card_name)
            await user_player.save(update_fields=['debuff'])

            msg = '' if len(card_slot) > 0 else ''

            msg = Message(
                at+MessageSegment.text(f'使用了【{card_name}】，目标为: ')+MessageSegment.at(target)+'\n')

        # 使用伤害卡片
        if card_name == '伤害':
            # 伤害倍率为2
            player.damage_rate = 2
            await player.save(update_fields=['damage_rate'])

            msg = Message(at+f' 使用了「{card_name}」，你感受到了一股强大的能量注入自己的大枪中~\n')

        # 使用后置卡片效果
        if card_name == '保护' or card_name == '伪装':

            player.buff.append(card_name)
            await player.save(update_fields=['buff'])

            msg = Message(
                at+MessageSegment.text(f'使用了【{card_name}】,喵叽酱会给你祝福的嗷~'))

        # 预言卡片
        if card_name == '预言':
            # 子弹位置
            current_bullet = record.current_bullet
            if current_bullet == -1:
                msg = Message(
                    at+MessageSegment.text(' 喵叽提醒你：这已经是最后一颗子弹了，你什么都看不到哦！'))
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

                msg = Message(
                    at+f' 使用了【{card_name}】，你似乎看到了枪管内部的结构：\n {bullet_str}\n')

        if card_name == '恢复':
            if player.life >= 3:
                msg = Message(
                    at+MessageSegment.text(f'使用了【{card_name}】，你的血量很棒，喵叽酱帮不了嗷~'))
            else:
                player.life += 1
                await player.save(update_fields=['life'])
                msg = Message(
                    at+MessageSegment.text(f'使用了【{card_name}】，生命值 up ⬆️，当前生命值：{player.life}'))

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
            return Message(MessageSegment.text(' 喵叽提醒：游戏不存在，请先开始战局！'))

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
            return Message(at+MessageSegment.text(' 喵叽提醒：当前不是你的回合，请等待'))

        # 更新玩家响应时间
        cls.set_scheduler(type=2, user_id=current_user_id, group_id=group_id)
        cls.set_scheduler(type=1, user_id=current_user_id, group_id=group_id)
        # 判断当前是否使用卡片回合
        if state != 5:
            # 抽卡阶段可以直接跳过，开始开枪
            if state == 3:
                record.state = 5
                await record.save(update_fields=['state'])
                # 直接开枪
                await cls.shoot(bot, event, at_group)
                return None
            return Message(at+MessageSegment.text(' 喵叽提醒：喵叽不认为现在你该开枪了！'))

        # 当前用户
        player = await RoulettePlayerTable.get_player(game_id=record.id, uid=user_id)

        # 如果不指定目标，则随机
        if len(at_group) == 0:
            # 随机一个目标，添加debuff
            target = str(random.choice(record.player_seat))
        else:
            target = str(at_group[0])

        if target not in record.player_seat:
            return Message(at+MessageSegment.text(' 喵叽提醒：不要试图攻击一个不在游戏中的无辜人嗷！'))

        # buff判定
        # 攻击倍率
        damage_rate = int(player.damage_rate)
        # 攻击目标
        user_player = await RoulettePlayerTable.get_player(game_id=record.id, uid=target)
        # 目标 buff
        buff = user_player.buff
        debuff = player.debuff
        # 获取子弹当前位置
        current_bullet = record.current_bullet
        # 获取子弹列表
        bullet_list = record.bullet_list

        bullet_type = bullet_list[current_bullet]

        # 子弹位置加1
        current_bullet = record.current_bullet
        current_bullet += 1

        if current_bullet > record.bullet_count - 1:
            current_bullet = -1
        record.current_bullet = current_bullet
        await record.save(update_fields=['current_bullet'])
        msg = ''
        # debuff 生效阶段，强制只能攻击自己
        if '强制' in debuff:
            target = user_id
            msg = '你感受到了一股强大的力量控制了自己的手\n'
            player.debuff.remove('强制')
            user_player = await RoulettePlayerTable.get_player(game_id=record.id, uid=target)
            await player.save(update_fields=['debuff'])

        user_at = MessageSegment.at(target)

        if str(target) == str(user_id):
            msg += '你颤颤巍巍的将枪顶住自己的脑门，扣下了扳机！只听 “啪” 一声！'
        else:
            msg = MessageSegment.text('你意气风发的将枪抵在了 ') + \
                user_at+MessageSegment.text(' 的脑门，说：再见了朋友！')

        await asyncio.sleep(1)
        await bot.send(event=event, message=msg)

        # 空弹自己
        if bullet_type == 0 and str(target) == str(user_id):
            await bot.send(event=event, message=at+' 谢天谢地是空弹，接下来还是我的回合！')

            if current_bullet == -1:
                record.state = 0

            # 更新数据
            await record.save(update_fields=['state'])

            # 开枪后，伤害归1
            player.damage_rate = 1
            await player.save(update_fields=['damage_rate'])

            # 进入下一个流程
            await cls.game_flowing(bot, event)
            return None

        # 空弹别人
        if bullet_type == 0 and str(target) != str(user_id):
            await bot.send(event=event, message=user_at+' 谢天谢地是空弹，到我了，宝贝儿！')
            # 只要是换人，都从 0 开始
            record.state = 0
            # 当前参赛人员
            player_seat = record.player_seat[:]
            # 获取下一个人
            next_current_id = cls.get_next_id(
                player_seat, record.current_user_id)
            print('next_current_id', next_current_id)
            # 换人
            if len(at_group) > 0:
                record.current_user_id = at_group[0]
            else:
                record.current_user_id = next_current_id

            # 开枪后，伤害归1
            player.damage_rate = 1
            await player.save(update_fields=['damage_rate'])

            await record.save(update_fields=['state', 'current_user_id'])
            await cls.game_flowing(bot, event)
            return None

        # buff 优先级 伤害转移 > 保护
        if '伪装' in buff:
            # 移除当前用户卡片效果
            buff.remove('伪装')
            user_player.buff = buff
            await user_player.save(update_fields=['buff'])

            # 判定伤害转移
            target = random.choice(record.player_seat)
            new_player = await RoulettePlayerTable.get_player(game_id=record.id, uid=target)
            new_at = MessageSegment.at(target)
            msg = user_at + \
                MessageSegment.text(' 使用了伪装，伤害转移给了') + \
                new_at + MessageSegment.text('\n')

            new_player.life -= damage_rate
            if new_player.life <= 0:
                new_player.life = 0

            if damage_rate > 1:
                msg += f'【伤害】效果触发，造成 {damage_rate} 倍伤害！\n'

            # 开枪后，伤害归1
            player.damage_rate = 1
            await player.save(update_fields=['damage_rate'])
            await new_player.save(update_fields=['life', 'damage_rate'])

            # 当前参赛人员
            player_seat = record.player_seat[:]

            if new_player.life == 0:
                msg += new_at + '被 '+at+' 击中，生命被清空，遗憾出局！\n'
                # 移除出局的玩家
                record.player_seat.remove(target)
                await record.save(update_fields=['player_seat'])
                new_player.status = 2
                await new_player.save(update_fields=['status'])
            else:
                msg += new_at + f' 剩余 {new_player.life} 命。\n'

            await bot.send(event=event, message=msg)

            # 判断是否回合结束
            # 如果达到了自己，回合结束
            if str(target) == str(user_id):
                # 获取下一个人
                next_current_id = cls.get_next_id(
                    player_seat, record.current_user_id)
                # 换人
                record.current_user_id = next_current_id
                record.state = 0
                await record.save(update_fields=['current_user_id', 'state'])
                # 进入下一个流程
                record.state = 0
            else:
                # 如果是打的别人，继续自己的回合
                if current_bullet == -1:
                    record.state = 0
                await record.save(update_fields=['state'])
            await cls.game_flowing(bot, event)

            return None
        elif '保护' in buff:
            # 移除当前用户卡片效果
            
            buff.remove('保护')
            user_player.buff = buff
            await user_player.save(update_fields=['buff'])

            # 开枪后，伤害归1
            player.damage_rate = 1
            await player.save(update_fields=['damage_rate'])

            msg = user_at + \
                MessageSegment.text(' 使用了【保护】，避免了伤害。这一波，我在第十层！\n')

            await bot.send(event=event, message=msg)

            # 当前参赛人员
            player_seat = record.player_seat[:]
            # 获取下一个人
            next_current_id = cls.get_next_id(
                player_seat, record.current_user_id)
            print('next_current_id', next_current_id)
            # 换人
            record.current_user_id = next_current_id
            record.state = 0

            await record.save(update_fields=['current_user_id', 'state'])
            # 进入下一个流程
            await cls.game_flowing(bot, event)
            return None
        else:
            # 没有buff 直接造成伤害
            user_player.life -= damage_rate
            if user_player.life <= 0:
                user_player.life = 0
            msg = ''
            if damage_rate > 1:
                msg += f' 【伤害】效果触发，造成 {damage_rate} 倍伤害！\n'

            # 开枪后，伤害归1
            player.damage_rate = 1
            await player.save(update_fields=['damage_rate'])
            await user_player.save(update_fields=['life'])

            # 当前参赛人员
            player_seat = record.player_seat[:]

            if user_player.life == 0:
                msg += user_at + f'被 '+at+' 击中，生命被清空，遗憾出局！'
                # 移除出局的玩家
                record.player_seat.remove(target)
                await record.save(update_fields=['player_seat'])
                user_player.status = 2
                await user_player.save(update_fields=['status'])
            else:
                msg += user_at + '被 '+at+f' 击中，剩余 {user_player.life} 命\n'

            await bot.send(event=event, message=msg)
            print('target', target)
            print('user_id', user_id)
            # 如果达到了自己，回合结束
            if str(target) == str(user_id):
                # 获取下一个人
                next_current_id = cls.get_next_id(
                    player_seat, record.current_user_id)
                print('next_current_id', next_current_id)
                # 换人
                record.current_user_id = next_current_id
                record.state = 0
                await record.save(update_fields=['current_user_id', 'state'])
                # 进入下一个流程
                await cls.game_flowing(bot, event)
            else:
                # 如果是打的别人，继续自己的回合
                if current_bullet == -1:
                    record.state = 0
                await record.save(update_fields=['state'])

                await cls.game_flowing(bot, event)

            return None

    @classmethod
    def game_help_rule(cls):
        """
        游戏注意事项
        """
        msg = (
            f'注意事项\n\n'
            f'1. 玩家在游戏开始后，每个回合对会有系统指引，正常按照指引操作即可。\n'
            f'2. 游戏中会有大量文本，建议在群聊人少的时候进行游戏。\n'
            f'3. 一场游戏大概 5-10 分钟左右。\n'
            f'4. 喵叽轮盘赌最少2人，最多5人进行游戏。\n'
            f'5. 同一个群统一时间只允许存在一个游戏。\n'
            f'6. 每个玩家卡包只有4个位置，如卡包已满，则无法获取新卡片。\n'
            f'7. 每个玩家只有3条命，先没先走。\n'
            f'8. 游戏开始后 10 分钟无响应则自动结束。\n'
            f'9. 游戏开始后，玩家2分钟无响应则做挂机处理，给于严厉处罚。\n'
        )
        img = txt2img(msg=msg)
        msg = MessageSegment.image(img)

        return msg

    @classmethod
    def game_help_flowing(cls):
        """
        游戏流程
        """
        msg = (
            '游戏流程说明\n\n'
            '1. 开启游戏战局，此时需要等待玩家加入。\n'
            '2. 玩家加入游戏，最多5人，最少2人。\n'
            '3. 游戏正式开始，此阶段会随机给玩家排序。\n'
            '4. 每人随机派发2张卡片 ，如枪内有子弹，则跳过本阶段。\n'
            '5. debuff 卡片效果判定阶段 （限制、强制类的卡片需要在此阶段判定）。\n'
            '6. 使用卡包专用存在的卡片，每次只能使用一张卡片，且一个回合内，只有当前阶段才能使用卡片。\n'
            '7. 即时 buff 卡片效果判定阶段 （伤害、恢复、预言类卡片需要在此阶段判定）。\n'
            '8. 开枪，此阶段每回合只有一次，可以对自己或是对别人亦或是全随机。\n'
            '9. 延后 buff 卡片效果判定（保护、伪装类卡片需要在此阶段判定）。\n'
            '10.持枪者判:\n'
            '   10.1. 对自己开枪：未中，则继续自己的回合。\n'
            '   10.2. 对自己开枪：中枪，则失去一条命，持枪者变更为下家。\n'
            '   10.3. 对外开枪：未中，则对家为新的持枪者。\n'
            '   10.4. 对外开枪：中枪，则对家失去一条命，继续自己的回合。\n'
            '11.结束回合 - 回到 4 阶段。\n'
        )
        img = txt2img(msg=msg, width=30)
        msg = MessageSegment.image(img)

        return msg
    @classmethod
    def game_help_card(cls):
        """
        卡片效果
        """
        msg = (
            '游戏卡片效果说明\n'
            '本赛季一共有 7 个卡片。\n\n'
            '1.即时卡片，使用后马上可以看到效果。\n'
            '   - 恢复：使用后，生命值 +1。\n'
            '   - 预言：可以查看最近枪内是否有子弹。\n'
            '2.延迟卡片，开枪后触发卡片效果。\n'
            '   - 保护：保护玩家免受伤害，下次受伤时生效。\n'
            '   - 伪装：受伤时转移给他人，有概率还是自己，下次受伤时生效。\n'
            '3.延迟卡片，回合开始时触发卡片效果。\n'
            '   - 禁锢：限制玩家下一回合的操作，不能使用卡片，不能有任何操作。\n'
            '   - 强制：强制下一个持枪者只能对自己开枪。\n'
            '4.伤害卡片，开枪时触发卡片效果。\n'
            '   - 伤害：对玩家造成双倍伤害。\n'

        )
        img = txt2img(msg=msg, width=35)
        msg = MessageSegment.image(img)

        return msg
    
    @classmethod
    def game_help_instruct(cls):
        """
        游戏指令
        """
        msg = (
            '游戏指令\n\n'
            '1. 创建游戏战局，可用指令：\n'
            '   /创建战局\n'
            '   /想跟姐妹来一场愉悦の拼刺刀嘛\n'
            '   /想不想来一场刺激的对枪运动\n'
            '   简化- /c (created)\n'
            '2. 手动结束游戏，可用指令：\n'
            '   /结束战局\n'
            '   /都踏马别玩啦\n'
            '   /有内奸终止交易\n'
            '   简化- /e (end)\n'
            '3. 玩家参与游戏，可用指令：\n'
            '   /参与战局\n'
            '   /我也要玩\n'
            '   /我要参加入\n'
            '   /都别动让我来\n'
            '   简化- /j (join)\n'
            '4. 开始游戏，可用指令：\n'
            '   /开始战局\n'
            '   /轮盘启动\n'
            '   /预备开始\n'
            '   简化- /s (start)\n'
            '5. 使用卡片buff，可用指令：\n'
            '   /使用卡片 [卡片名称]\n'
            '   /使用卡牌 [卡片名称]\n'
            '   /就你了 [卡片名称]\n'
            '   /吃我一招 [卡片名称]\n'
            '   /使用 [卡片名称]\n'
            '   /用卡 [卡片名称]\n'
            '   简化- /u (use)\n'
            '6. 跳过出卡阶段，可用指令：\n'
            '   /跳过\n'
            '   /过\n'
            '   /skip\n'
            '   简化- /p (pass)\n'
            '7. 开枪，可用指令：\n'
            '   /开枪\n'
            '   /peng\n'
            '   /pa\n'
            '8. 查询信息，查询流程，可用指令：\n'
            '   /查询 \n'
            '   /查询 流程\n'
            '   简化- /q (query)\n'
            '9. 帮助信息，可用指令：\n'
            '   /帮助 \n'
            '   简化- /h (help)\n'

        )
        img = txt2img(msg=msg, width=30)
        msg = MessageSegment.image(img)

        return msg

    @classmethod
    def get_next_id(cls, player_seat, current_id):
        """
        获取下一个索引
        """

        current_index = player_seat.index(current_id)
        next_index = (current_index + 1) % len(player_seat)
        # 是否指定了人
        return player_seat[next_index]

    @classmethod
    async def auto_game(cls, type: int, user_id: str, group_id: str):
        """
        自动游戏流程
        """
        task_id = f"{user_id}_{group_id}_{type}"
        bot: Bot = get_bot()
        # 游戏长时间无响应
        if type == 1:
            # 整体游戏流程
            msg = await cls.close_game(group_id=group_id, user_id=user_id, auto_end=True)
            await bot.send_group_msg(group_id=int(group_id), message=msg)

        # 个人长时间无响应
        elif type == 2:
            print(f'长时间无响应 {task_id}')
            record = await RouletteGameTable.get_game(group_id)
            if record:
                player = await RoulettePlayerTable.get_player(game_id=record.id, uid=user_id)
                at = MessageSegment.at(user_id)
                msg = at + ' 长时间无响应，喵叽酱觉得你在挂机，给你一点小惩罚，扣你2滴血！\n'

                player.life -= 2
                if player.life <= 0:
                    player.life = 0
                 # 开枪后，伤害归1
                player.damage_rate = 1
                await player.save(update_fields=['life', 'damage_rate'])

                # 当前参赛人员
                player_seat = record.player_seat[:]

                if player.life == 0:
                    msg += at + ' 因挂机被制裁了，生命被清空，遗憾出局！\n'
                    # 移除出局的玩家
                    if user_id in record.player_seat:
                        record.player_seat.remove(user_id)
                        await record.save(update_fields=['player_seat'])
                    player.status = 2
                    await player.save(update_fields=['status'])
                else:
                    msg += at + f' 剩余 {player.life} 命。\n'

                await bot.send_group_msg(group_id=int(group_id), message=msg)

                next_current_id = cls.get_next_id(
                    player_seat, record.current_user_id)
                # 换人
                record.current_user_id = next_current_id
                record.state = 0

                await record.save(update_fields=['state', 'current_user_id'])

                await cls.game_flowing(user_id=user_id, group_id=group_id)
            else:
                print('游戏不存在')

    @classmethod
    def set_scheduler(cls, type: int, user_id: str, group_id: str):
        """
        设置定时任务
        参数：
            - type: 任务类型  1. 整体游戏流程 2. 用户回合
            - user_id: 用户ID
            - group_id: 群ID
            - time: 时间
        """
        # 任务id
        task_id = f"{group_id}_{type}"
        # 检查任务是否存在
        if scheduler.get_job(task_id):
            # 如果任务存在，删除它
            try:
                scheduler.remove_job(task_id)
            except Exception as e:
                logger.warning(f"停止任务错误 {task_id}: {e}")
        else:
            logger.warning(f"{task_id} 无任务")

        # 响应时间
        time = 1
        if type == 1:
            time = GAME_RESPONSE_TIME
        if type == 2:
            time = PLAYER_RESPONSE_TIME

        # 创建定时任务
        try:
            # 计算三分钟后的时间
            run_time = datetime.now() + timedelta(minutes=time)
            scheduler.add_job(
                cls.auto_game,
                "date",  # 触发器类型，"date" 表示在指定的时间只执行一次
                run_date=run_time,  # 执行时间
                args=[type, user_id, group_id],  # 传递给 函数的参数
                id=task_id,  # 任务 ID，需要确保每个任务的 ID 是唯一的
            )
            logger.success(f"{task_id} 轮盘赌定时任务添加成功")
        except ActionFailed as e:
            logger.warning(f"{task_id} 定时任务添加失败，{repr(e)}")

    @classmethod
    def end_scheduler(cls, task_id):
        # 检查任务是否存在
        if scheduler.get_job(task_id):
            # 如果任务存在，删除它
            try:
                scheduler.remove_job(task_id)
                print(f'已经停止游戏定时任务： {task_id}')
            except Exception as e:
                logger.warning(f"停止游戏任务错误 {task_id}: {e}")
        else:
            logger.warning(f"{task_id} 无任务")
