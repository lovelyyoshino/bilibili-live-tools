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
    await bilibili().apppost_heartbeat()


async def pcpost_heartbeat():
    await bilibili().pcpost_heartbeat()


async def heart_gift():
    await bilibili().heart_gift()


# 因为休眠时间差不多,所以放到这里,此为实验性功能
async def draw_lottery():
    for i in range(68, 90):
        response = await bilibili().get_lotterylist(i)
        json_response = await response.json()
        if json_response['code'] == 0:
            temp = json_response['data']['title']
            if "测试" in temp:
                print("检测到疑似钓鱼类测试抽奖，默认不参与，请自行判断抽奖可参与性")
                # print(url)
            else:
                check = len(json_response['data']['typeB'])
                for g in range(0, check):
                    join_end_time = json_response['data']['typeB'][g]['join_end_time']
                    join_start_time = json_response['data']['typeB'][g]['join_start_time']
                    ts = CurrentTime()
                    if int(join_end_time) > int(ts) > int(join_start_time):
                        response1 = await bilibili().get_gift_of_lottery(i, g)
                        json_response1 = await response1.json()
                        print("当前时间:", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                        print("参与实物抽奖回显：", json_response1)
                    else:
                        pass
        else:
            break


async def run():
    while 1:
        Printer().printlist_append(['join_lottery', '', 'user', "心跳"], True)
        if login.check_token():
            pass
        else:
            login.refresh_token()
        await apppost_heartbeat()
        await pcpost_heartbeat()
        await heart_gift()
        await draw_lottery()
        await asyncio.sleep(300)


