from bilibili import bilibili
import time
import datetime
import asyncio
from printer import Printer
from bilitimer import BiliTimer
import login


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return str(currenttime)


async def apppost_heartbeat():
    if login.check_token():
        pass
    else:
        login.RefreshToken()
    json_response = await bilibili().apppost_heartbeat()
    # print('apppost_heartbeat', json_response)
    Printer().printlist_append(['join_lottery', '', 'user', "心跳"], True)
    BiliTimer().append2list_jobs([apppost_heartbeat, [], int(CurrentTime()), 300])


async def pcpost_heartbeat():
    json_response = await bilibili().pcpost_heartbeat()
    # print('pcpost_heartbeat', json_response)
    BiliTimer().append2list_jobs([pcpost_heartbeat, [], int(CurrentTime()), 300])


async def heart_gift():
    json_response =  await bilibili().heart_gift()
    # print('heart_gift', json_response)
    BiliTimer().append2list_jobs([heart_gift, [], int(CurrentTime()), 300])


# 因为休眠时间差不多,所以放到这里,此为实验性功能
async def draw_lottery():
    for i in range(68, 90):
        json_response = await bilibili().get_lotterylist(i)
        # -400 不存在
        if json_response['code'] == 0:
            temp = json_response['data']['title']
            if "测试" in temp or 'test' in temp:
                print("检测到疑似钓鱼类测试抽奖，默认不参与，请自行判断抽奖可参与性")
                # print(url)
            else:
                check = len(json_response['data']['typeB'])
                for g in range(0, check):
                    join_end_time = json_response['data']['typeB'][g]['join_end_time']
                    join_start_time = json_response['data']['typeB'][g]['join_start_time']
                    ts = CurrentTime()
                    if int(join_end_time) > int(ts) > int(join_start_time):
                        json_response1 = await bilibili().get_gift_of_lottery(i, g)
                        print("当前时间:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                        print("参与实物抽奖回显：", json_response1)
                    else:
                        pass
        else:
            break
    BiliTimer().append2list_jobs([draw_lottery, [], int(CurrentTime()), 300])

        
def init():
    BiliTimer().append2list_jobs([apppost_heartbeat, [], 0, 0])
    BiliTimer().append2list_jobs([pcpost_heartbeat, [], 0, 0])
    BiliTimer().append2list_jobs([heart_gift, [], 0, 0])
    BiliTimer().append2list_jobs([draw_lottery, [], 0, 0])


