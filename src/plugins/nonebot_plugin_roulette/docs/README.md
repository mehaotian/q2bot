# 群轮盘赌

使用签到金币作为筹码的群轮盘赌插件

## 游戏方式

通过指令进行游戏，每次游戏为了避免其他人乱入，需要创建 战局， 玩家需要战局后才能进行游戏，无加入战局的玩家，输入任何指令都将不会生效。

## 开启战局

发起人需要发送指令 `/开盘 [筹码] [实弹数量（最少为玩家数量-1）]` 开启战局，开启战局后，所有玩家都可以参与游戏，但是只有发起人和管理员可以结束战局。

一次战局 最少两人参与，最多5人参与，每次只允许存在一个战局，其他人只能观战，但是可以参与盘口赌注，如果战局结束，所有玩家都可以重新开始新的战局。

## 参与游戏

玩家可以发送指令 `/加入` 加入战局，如果战局未开启，则无法加入

接下来游戏阶段会按照如下顺序进行

### 1. 开始回合

待所有玩家参与战局后或准备好后，发起人可以发送指令 `/开始` 开始战局

游戏开始后，系统会roll出一个随机顺序，按照顺序进行游戏，每个玩家可以进行下面的操作

### 2. 押注 （先不做）

当前阶段所有玩家都可以发送指令 `/押 [玩家编号] [筹码]` 下注.

- 赢：如果押中的玩家赢得胜利，所有押赢的玩家平分输家所有筹码
- 输：如果押中的玩家输掉比赛，所有押输的玩家将失去所有筹码

## 玩家回合

此时进行玩家回合，此回合中，会产生一个持枪者，持枪者会进行如下操作：

- 抽卡
- 使用卡片
- 开枪

### 抽卡

玩家每次成为持枪者后，会有一次抽卡机会。
玩家需从卡片池中抽取2张卡片，放入卡片背包，每人卡片背包最多存放四张卡片，如背包已满，则新抽卡片废弃。

### 使用卡片

当玩家背包有可使用卡片时，可以选择使用卡片，卡片效果会在比赛中生效。

当玩家背包无可使用卡片时，或者选择 pass 时，自动跳过当前阶段，进入下一个阶段

### 开枪

此时玩家有2个选择，对自己开枪，或随机对外开枪，此时会发生如下情况：

- 对自己开枪：未中，则继续自己的回合
- 对自己开枪：中枪，则失去一条命，持枪者变更为下家

- 对外开枪：未中，则对家为新的持枪者
- 对外开枪：中枪，则对家失去一条命，继续自己的回合

## 结束战局

正常来说，每人三条命，当玩家失去所有生命值时，玩家将被淘汰，剩余玩家继续比赛，直到只剩下一名玩家。

获胜者将获得所有筹码，战局结束，所有玩家可以重新开始新的战局。

## 卡片效果描述

### 类型

卡片类型决定了卡片的效果，目前有以下几种类型：
**卡片实时效果**

- 恢复：恢复玩家一格生命值
- 预言：可以查看最近枪内是否有子弹

**开枪判定**

- 保护：保护玩家免受伤害，下次受伤时生效
- 伪装：受伤时转移给他人，有概率还是自己，下次受伤时生效
- 伤害：对玩家造成双倍伤害

**回合开始判定**

- 禁锢：限制玩家下一回合的操作，不能使用卡片，不能有任何操作
- 强制：强制下一个持枪者只能对自己开枪

## 流程图

- 1. 开局
- 2. 加入
- 3. 开始 - 系统装弹，随机抽取一名玩家作为持枪者，没人随机派发四张卡片
- 4. 派发抽卡 ，如枪内有子弹，则跳过本阶段
- 5. 卡片判定 （限制、强制类的卡片需要在此阶段判定）
- 6. 使用卡片
- 7. 卡片判定 （伤害、恢复、预言类卡片需要在此阶段判定）
- 8. 开枪
- 9. 卡片判定（保护、伪装类卡片需要在此阶段判定）
- 10.持枪者判定，
  - 10.1. 对自己开枪：未中，则继续自己的回合
  - 10.2. 对自己开枪：中枪，则失去一条命，持枪者变更为下家
  - 10.3. 对外开枪：未中，则对家为新的持枪者
  - 10.4. 对外开枪：中枪，则对家失去一条命，继续自己的回合
- 10.结束回合 - 回到 3阶段

```base

玩家1： /开启一场精彩的轮盘赌吧
系统：@玩家1 开启了一场精彩的轮盘赌，快来参与吧，输入 /参与战局 参与游戏
玩家2： /参与战局
系统：@玩家2 参与了游戏，等待其他玩家参与或等待发起人开始游戏
玩家3： /参与战局
系统：@玩家3 参与了游戏，等待其他玩家参与或等待发起人开始游戏
玩家1： /开始游戏
系统：@玩家1 @玩家2 @玩家3  精彩刺激的轮盘赌开始了哦，系统随机抽取一名玩家作为持枪者，所有玩家注意自己的座位
系统：座位顺序为：玩家1 -> 玩家3 -> 玩家2
系统：开始抽卡
系统：@玩家1 你的卡片为：[卡片1] [卡片2] [卡片3] [卡片4]
系统：@玩家2 你的卡片为：[卡片1] [卡片2] [卡片3] [卡片4]
系统：@玩家3 你的卡片为：[卡片1] [卡片2] [卡片3] [卡片4]
系统：自己回合使用卡片" /使用卡片 [牌号]" 或者输入 "/pass " 跳过本阶段
系统：所有玩家回合结束，开始持枪者回合
系统：@玩家1 你是本轮的持枪者，当前无卡片判定，是否使用卡片？
玩家1： /使用卡片 1
系统：@玩家1 使用了卡片1，效果生效，@玩家3 被禁锢，下一回合无法行动，是否继续使用卡片？
玩家1： /pass
系统：@玩家1 是否开枪？
玩家1： /开枪
系统：@玩家1 对自己开枪，未中枪，继续自己的回合，是否开枪？
玩家1： /开枪 @玩家3
系统：@玩家1 对 @玩家3 凶猛的开了一枪，他打中了，我的上帝啊
系统：@玩家3 失去一条命，继续自己的回合，是否开枪？
玩家1： /开枪
系统：@玩家1 对自己开枪，中枪，失去一条命，持枪者变更为 @玩家3
系统：@玩家3 你是本轮的持枪者，现在开始进行卡片判定。
系统：@玩家3 限制卡片生效，您失去了行动能力，持枪者变更为 @玩家2
系统：@玩家2 你是本轮的持枪者，当前无卡片判定，是否使用卡片。
玩家2： /pass
...

系统：6发子弹并没带走任何人，开始重新填装弹夹。
系统：开始派发卡片
系统：@玩家1 你的卡片为：[卡片1] [卡片2] [卡片3] [卡片4]
系统：@玩家2 你的卡片为：[卡片1] [卡片2] [卡片3] [卡片4]
系统：@玩家3 你的卡片为：[卡片1] [卡片2] [卡片3] [卡片4]

系统：@玩家1 是本轮的持枪者，当前无卡片判定，是否使用卡片？
玩家1： /使用卡片 预言
系统：@玩家1 使用了预言卡片，你看了一眼枪内，发现了子弹，是否继续使用卡片？
玩家1： /pass
系统：@玩家1 是否开枪？
玩家1： /开枪 @玩家2
系统：@玩家1 对 @玩家2 凶猛的开了一枪，他打中了，@玩家2 连中三枪，已经无力回天，被淘汰
系统：@玩家2 被淘汰，继续自己的回合，是否开枪？
...

系统：@玩家1 获得了胜利，获得了所有筹码，战局结束，所有玩家可以重新开始新的战局。

```