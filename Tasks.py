from bilibili import bilibili
import asyncio
from configloader import ConfigLoader
import utils
import printer
from bilitimer import BiliTimer
import random
import re
import json

# 获取每日包裹奖励
async def Daily_bag():
    json_response = await bilibili.get_dailybag()
    # no done code
    printer.warn(json_response)
    for i in json_response['data']['bag_list']:
        printer.info(["# 获得-" + i['bag_name'] + "-成功"])
    await BiliTimer.append2list_jobs(Daily_bag, 21600)


# 签到功能
async def DoSign():
    # -500 done
    temp = await bilibili.get_dosign()
    printer.warn(temp)
    printer.info([f'# 签到状态: {temp["msg"]}'])
    if temp['code'] == -500 and '已' in temp['msg']:
        sleeptime = (utils.seconds_until_tomorrow() + 300)
    else:
        sleeptime = 350
    await BiliTimer.append2list_jobs(DoSign, sleeptime)

# 领取每日任务奖励
async def Daily_Task():
    # -400 done/not yet
    json_response2 = await bilibili.get_dailytask()
    printer.warn(json_response2)
    printer.info([f'# 双端观看直播:  {json_response2["msg"]}'])
    if json_response2['code'] == -400 and '已' in json_response2['msg']:
        sleeptime = (utils.seconds_until_tomorrow() + 300)
    else:
        sleeptime = 350
    await BiliTimer.append2list_jobs(Daily_Task, sleeptime)

async def Sign1Group(i1, i2):
    json_response = await bilibili.assign_group(i1, i2)
    if not json_response['code']:
        if json_response['data']['status']:
            printer.info([f'# 应援团 {i1} 已应援过'])
        else:
            printer.info([f'# 应援团 {i1} 应援成功,获得 {json_response["data"]["add_num"]} 点亲密度'])
    else:
        printer.info([f'# 应援团 {i1} 应援失败'])

# 应援团签到
async def link_sign():
    json_rsp = await bilibili.get_grouplist()
    printer.warn(json_rsp)
    list_check = json_rsp['data']['list']
    id_list = ((i['group_id'], i['owner_uid']) for i in list_check)
    if list_check:
        tasklist = []
        for (i1, i2) in id_list:
            task = asyncio.ensure_future(Sign1Group(i1, i2))
            tasklist.append(task)
        results = await asyncio.gather(*tasklist)
    await BiliTimer.append2list_jobs(link_sign, 21600)

async def send_gift():
    if ConfigLoader().dic_user['task_control']['clean-expiring-gift']:
        argvs = await utils.fetch_bag_list(show=False)
        printer.warn(argvs)
        roomID = ConfigLoader().dic_user['task_control']['clean-expiring-gift2room']
        time_set = ConfigLoader().dic_user['task_control']['set-expiring-time']
        list_gift = []
        for i in argvs:
            left_time = i[3]
            if left_time is not None and 0 < int(left_time) < time_set:  # 剩余时间少于半天时自动送礼
                list_gift.append(i[:3])
        if list_gift:
            print('发现即将过期的礼物')
            if ConfigLoader().dic_user['task_control']['clean_expiring_gift2all_medal']:
                print('正在投递其他勋章')
                list_medal = await utils.fetch_medal(show=False)
                list_gift = await full_intimate(list_gift, list_medal)
                
            print('正在清理过期礼物到指定房间')
            for i in list_gift:
                giftID = i[0]
                giftNum = i[1]
                bagID = i[2]
                await utils.send_gift_web(roomID, giftNum, bagID, giftID)
        else:
            print('未发现即将过期的礼物')
    await BiliTimer.append2list_jobs(send_gift, 21600)

async def auto_send_gift():
    # await utils.WearingMedalInfo()
    # return
    list_medal = []
    if ConfigLoader().dic_user['task_control']['send2wearing-medal']:
        list_medal = await utils.WearingMedalInfo()
        if not list_medal:
            print('暂未佩戴任何勋章')
            # await BiliTimer.append2list_jobs(auto_send_gift, 21600)
    if ConfigLoader().dic_user['task_control']['send2medal']:
        list_medal += await utils.fetch_medal(False, ConfigLoader().dic_user['task_control']['send2medal'])
    # print(list_medal)    
    print('正在投递勋章')
    temp = await utils.fetch_bag_list(show=False)
    # print(temp)
    list_gift = []
    for i in temp:
        gift_id = int(i[0])
        left_time = i[3]
        if (gift_id not in [4, 3, 9, 10]) and left_time is not None:
            list_gift.append(i[:3])
    await full_intimate(list_gift, list_medal)
            
    # printer.info(["# 自动送礼共送出亲密度为%s的礼物" % int(calculate)])
    await BiliTimer.append2list_jobs(auto_send_gift, 21600)

async def full_intimate(list_gift, list_medal):
    json_res = await bilibili.gift_list()
    dic_gift = {j['id']: (j['price'] / 100) for j in json_res['data']}
    for roomid, left_intimate, medal_name in list_medal:
        calculate = 0
        # print(list_gift)
        for i in list_gift:
            gift_id, gift_num, bag_id = i
            # print(gift_id, bag_id)
            if (gift_num * dic_gift[gift_id] <= left_intimate):
                pass
            elif left_intimate - dic_gift[gift_id] >= 0:
                gift_num = int((left_intimate) / (dic_gift[gift_id]))
            else:
                continue
            i[1] -= gift_num
            score = dic_gift[gift_id] * gift_num
            await asyncio.sleep(1.5)
            await utils.send_gift_web(roomid, gift_num, bag_id, gift_id)
            calculate = calculate + score
            left_intimate = left_intimate - score
        printer.info([f'# 对{medal_name}共送出亲密度为{int(calculate)}的礼物'])
    return [i for i in list_gift if i[1]]


async def doublegain_coin2silver():
    if ConfigLoader().dic_user['task_control']['doublegain_coin2silver']:
        json_response0 = await bilibili.request_doublegain_coin2silver()
        json_response1 = await bilibili.request_doublegain_coin2silver()
        print(json_response0['msg'], json_response1['msg'])
    await BiliTimer.append2list_jobs(doublegain_coin2silver, 21600)

async def sliver2coin():
    if ConfigLoader().dic_user['task_control']['silver2coin']:
        # 403 done
        json_response1 = await bilibili.silver2coin_app()
        # -403 done
        json_response = await bilibili.silver2coin_web()
        printer.info([f'#  {json_response["msg"]}'])
        printer.info([f'#  {json_response1["msg"]}'])
        if json_response['code'] == -403 and '只' in json_response['msg']:
            finish_web = True
        else:
            finish_web = False

        if json_response1['code'] == 403 and '最多' in json_response1['msg']:
            finish_app = True
        else:
            finish_app = False
        if finish_app and finish_web:
            sleeptime = (utils.seconds_until_tomorrow() + 300)
            await BiliTimer.append2list_jobs(sliver2coin, sleeptime)
            return
        else:
            await BiliTimer.append2list_jobs(sliver2coin, 350)
            return

    await BiliTimer.append2list_jobs(sliver2coin, 21600)

async def GetVideoExp(list_topvideo):
    print('开始获取视频观看经验')
    aid = list_topvideo[random.randint(0, 19)]
    cid = await utils.GetVideoCid(aid)
    await bilibili().Heartbeat(aid, cid)

async def GiveCoinTask(coin_remain, list_topvideo):
    while coin_remain > 0:
        aid = random.choice(list_topvideo)
        rsp = await utils.GiveCoin2Av(aid, 1)
        if rsp is None:
            break
        elif rsp:
            coin_remain -= 1

async def GetVideoShareExp(list_topvideo):
    print('开始获取视频分享经验')
    aid = list_topvideo[random.randint(0, 19)]
    await bilibili().DailyVideoShare(aid)

async def BiliMainTask():
    login, watch_av, num, share_av = await utils.GetRewardInfo()
    if ConfigLoader().dic_user['task_control']['fetchrule'] == 'bilitop':
        list_topvideo = await utils.GetTopVideoList()
    else:
        list_topvideo = await utils.fetch_uper_video(ConfigLoader().dic_user['task_control']['mid'])
    if (not login) or not watch_av:
        await GetVideoExp(list_topvideo)
    coin_sent = (num) / 10
    coin_set = min((ConfigLoader().dic_user['task_control']['givecoin']), 5)
    coin_remain = coin_set - coin_sent
    await GiveCoinTask(coin_remain, list_topvideo)
    if not share_av:
        await GetVideoShareExp(list_topvideo)
    # b站傻逼有记录延迟，3点左右成功率高一点
    await BiliTimer.append2list_jobs(BiliMainTask, utils.seconds_until_tomorrow() + 10800)


async def check(id):
    # 3放弃
    # 2 否 voterule
    # 4 删除 votedelete
    # 1 封杀 votebreak
    text_rsp = await bilibili().req_check_voted(id)
    # print(response.text)
        
    pattern = re.compile(r'\((.+)\)')
    match = pattern.findall(text_rsp)
    temp = json.loads(match[0])
    # print(temp['data']['originUrl'])
    data = temp['data']
    print(data['originContent'])
    votebreak = data['voteBreak']
    voteDelete = data['voteDelete']
    voteRule = data['voteRule']
    voted = votebreak+voteDelete+voteRule
    if voted:
        percent = voteRule / voted
    else:
        percent = 0
    print('目前已投票', voted)
    print('认为不违反规定的比例', percent)
    vote = 3
    if voted >= 400:
        if percent >= 0.8:
            vote = 2
        elif percent <= 0.2:
            vote = 4
    elif voted >= 150:
        if percent >= 0.9:
            vote = 2
        elif percent <= 0.1:
            vote = 4
    elif voted >= 50:
        if percent >= 0.97:
            vote = 2
        elif percent <= 0.03:
            vote = 4
    return vote
 
               
async def judge():
    num_case = 0
    num_voted = 0
    while True:
        temp = await bilibili().req_fetch_case()
        if not temp['code']:
            id = temp['data']['id']
        else:
            print('本次未获取到案件')
            # await asyncio.sleep(1)
            break
        vote = await check(id)
        print('投票决策', id, vote)
        json_rsp = await bilibili().req_vote_case(id, vote)
        print(json_rsp)
        num_case += 1
        if vote != 3:
            num_voted += 1
        
        print('______________________________')
        # await asyncio.sleep(1)
    
    printer.info([f'风纪委员会共获取{num_case}件案例，其中有效投票{num_voted}件'], True)
    await BiliTimer.append2list_jobs(judge, 3600)
        

async def init():
    await BiliTimer.append2list_jobs(sliver2coin, 0)
    await BiliTimer.append2list_jobs(doublegain_coin2silver, 0)
    await BiliTimer.append2list_jobs(DoSign, 0)
    await BiliTimer.append2list_jobs(Daily_bag, 0)
    await BiliTimer.append2list_jobs(Daily_Task, 0)
    await BiliTimer.append2list_jobs(link_sign, 0)
    await BiliTimer.append2list_jobs(send_gift, 0)
    await BiliTimer.append2list_jobs(auto_send_gift, 0)
    await BiliTimer.append2list_jobs(BiliMainTask, 0)
    await BiliTimer.append2list_jobs(judge, 0)
    
