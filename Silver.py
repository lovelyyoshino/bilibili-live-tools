from bilibili import bilibili
import utils
from printer import Printer
from bilitimer import BiliTimer


# 领瓜子时判断领取周期的参数
async def time_start():

    temp = await bilibili().get_time_about_silver()
    # print (temp['code'])    #宝箱领完返回的code为-10017
    if temp['code'] == -10017:
        Printer().printlist_append(['join_lottery', '', 'user', "# 今日宝箱领取完毕"])
    else:
        time_start = temp['data']['time_start']
        time_end = temp['data']['time_end']
        return str(time_start), str(time_end)

# 领取银瓜子
async def GetAward():
    silver_time = await time_start()
    if silver_time is not None:
        timestart, timeend = silver_time
    else:
        return
    json_response = await bilibili().get_silver(timestart, timeend)
    return json_response

async def GetAllSilver():
    while 1:
        Printer().printlist_append(['join_lottery', '', 'user', "检查宝箱状态"], True)
        json_rsp = await GetAward()
        if json_rsp is None or json_rsp['code'] == -10017:
            sleeptime = (utils.seconds_until_tomorrow() + 300)
            BiliTimer().append2list_jobs([GetAllSilver, [], int(utils.CurrentTime()), sleeptime])
            return
        elif json_rsp['code'] == 0:
            Printer().printlist_append(['join_lottery', '', 'user', "# 打开了宝箱"])
        else:
            Printer().printlist_append(['join_lottery', '', 'user',"# 继续等待宝箱冷却..."])
            # 未来如果取消了这个东西就睡眠185s，否则精确睡眠
            # surplus里面是min，float格式
            sleeptime = (json_rsp['data'].get('surplus', 3)) * 60 + 5
            BiliTimer().append2list_jobs([GetAllSilver, [], int(utils.CurrentTime()), sleeptime])
            return

                                              
def init():
    BiliTimer().append2list_jobs([GetAllSilver, [], 0, 0])
