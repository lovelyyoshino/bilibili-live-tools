from bilibili import bilibili
import time
import datetime
import asyncio
from printer import Printer
import login


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return str(currenttime)


async def apppost_heartbeat():
    json_response = await bilibili.apppost_heartbeat()
    # print('apppost_heartbeat', json_response)


async def pcpost_heartbeat():
    json_response = await bilibili.pcpost_heartbeat()
    # print('pcpost_heartbeat', json_response)


async def heart_gift():
    json_response =  await bilibili.heart_gift()
    # print('heart_gift', json_response)


# 因为休眠时间差不多,所以放到这里,此为实验性功能
async def draw_lottery():
    for i in range(72, 90):
        json_response = await bilibili.get_lotterylist(i)
        blacklist = ['test', 'TEST', '测试', '加密']
        # -400 不存在
        if not json_response['code']:
            temp = json_response['data']['title']
            if any(word in temp for word in blacklist):
                print("检测到疑似钓鱼类测试抽奖，默认不参与，请自行判断抽奖可参与性")
                # print(temp)
            else:
                check = json_response['data']['typeB']
                for g, value in enumerate(check):
                    join_end_time = value['join_end_time']
                    join_start_time = value['join_start_time']
                    ts = CurrentTime()
                    if int(join_end_time) > int(ts) > int(join_start_time):
                        json_response1 = await bilibili.get_gift_of_lottery(i, g)
                        print("当前时间:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                        print("参与实物抽奖回显：", json_response1)
                    else:
                        pass
        else:
            break

        
async def run():
    while 1:
        Printer().printlist_append(['join_lottery', '', 'user', "心跳"], True)
        login.HandleExpire()
        await apppost_heartbeat()
        await pcpost_heartbeat()
        await heart_gift()
        await draw_lottery()
        await asyncio.sleep(300)


