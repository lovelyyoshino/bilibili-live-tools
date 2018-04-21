from bilibili import bilibili
import datetime
import asyncio
import utils
from printer import Printer


# 将time_end时间转换成正常时间
def DataTime():
    datatime = str(datetime.datetime.fromtimestamp(float(time_end())))
    return datatime

# 领瓜子时判断领取周期的参数
async def time_start():

    response = await bilibili().get_time_about_silver()
    temp = await response.json()
    # print (temp['code'])    #宝箱领完返回的code为-10017
    if temp['code'] == -10017:
        Printer().printlist_append(['join_lottery', '', 'user', "# 今日宝箱领取完毕"])
    else:
        time_start = temp['data']['time_start']
        return str(time_start)

# 领瓜子时判断领取周期的参数
async def time_end():
    try:
        response = await bilibili().get_time_about_silver()
        temp = await response.json()
        time_end = temp['data']['time_end']
        return str(time_end)
    except:
        pass

# 领取银瓜子
async def GetAward():
    try:
        timeend = await time_end()
        timestart = await time_start()
        response = await bilibili().get_silver(timestart, timeend)
        # print(response.json())
        json_response = await response.json()
        return json_response['code']
    except:
        pass

async def run():
    while 1:
        Printer().printlist_append(['join_lottery', '', 'user', "检查宝箱状态"], True)
        temp = await GetAward()
        if temp is None or temp == -10017:
            await asyncio.sleep(utils.seconds_until_tomorrow() + 300)
        elif temp == 0:
            Printer().printlist_append(['join_lottery', '', 'user', "# 打开了宝箱"])
            await GetAward()
        else:
            Printer().printlist_append(['join_lottery', '', 'user',"# 继续等待宝箱冷却..."])
            await asyncio.sleep(181)
