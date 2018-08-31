from bilibili import bilibili
from statistics import Statistics
import printer
import utils
import asyncio
import time
import random
from bilitimer import BiliTimer


def CurrentTime():
    currenttime = int(time.time())
    return currenttime


class Rafflehandler:
    __slots__ = ('queue_raffle', 'list_raffle_id')
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Rafflehandler, cls).__new__(cls, *args, **kw)
            cls.instance.queue_raffle = asyncio.Queue()
            cls.instance.list_raffle_id = []
        return cls.instance
        
    async def run(self):
        while True:
            raffle = await self.queue_raffle.get()
            await asyncio.sleep(0.5)
            list_raffle0 = [self.queue_raffle.get_nowait() for i in range(self.queue_raffle.qsize())]
            list_raffle0.append(raffle)
            list_raffle = list(set(list_raffle0))
                
            # print('过滤完毕')
            # if len(list_raffle) != len(list_raffle0):
            # print('过滤机制起作用')
            
            tasklist = []
            for i in list_raffle:
                i = list(i)
                i[0] = list(i[0])
                for j in range(len(i[0])):
                    if isinstance(i[0][j], tuple):
                        # print('检测')
                        # i[0] = list(i[0])
                        i[0][j] = await i[0][j][1](*(i[0][j][0]))
                # print(i)
                task = asyncio.ensure_future(i[1](*i[0]))
                tasklist.append(task)
            
            # await asyncio.wait(tasklist, return_when=asyncio.ALL_COMPLETED)
            
    @staticmethod
    def Put2Queue(value, func):
        # print('welcome to appending')
        Rafflehandler.instance.queue_raffle.put_nowait((value, func))
        # print('appended')
        return
        
    @staticmethod
    async def Put2Queue_wait(value, func):
        # print('welcome to appending')
        await Rafflehandler.instance.queue_raffle.put((value, func))
        # print('appended')
        return
            
    @staticmethod
    def getlist():
        print('目前TV任务队列状况', Rafflehandler.instance.queue_raffle.qsize())
        
    def add2raffle_id(self, raffle_id):
        self.list_raffle_id.append(raffle_id)
        if len(self.list_raffle_id) > 150:
            # print(self.list_raffle_id)
            del self.list_raffle_id[:75]
            # print(self.list_raffle_id)
    
    def check_duplicate(self, raffle_id):
        return (raffle_id in self.list_raffle_id)
        

async def handle_1_TV_raffle(num, real_roomid, raffleid, raffle_type):
    while True:
        json_response2 = await bilibili.get_gift_of_TV_app(real_roomid, raffleid, raffle_type)
        code = json_response2['code']
        if not code:
            break
        elif code == -403:
            return True
        elif code == -405:
            print('没抢到。。。。。')
            printer.warn(f'{raffleid}  {raffle_type} {num}')
            return False
        elif code == 400:
            print(json_response2)
            return
            tasklist = []
            for i in range(60):
                task = asyncio.ensure_future(handle_1_TV_raffle_black(num, real_roomid, raffleid, raffle_type))
                tasklist.append(task)
            await asyncio.wait(tasklist, return_when=asyncio.FIRST_COMPLETED)
            return
        elif code != -401 and code != -403:
            pass
        print('如果循环请联系作者', num, real_roomid, raffleid, raffle_type)
        
    data = json_response2['data']
    Statistics.append_to_TVlist(raffleid, real_roomid)
    Statistics.add_to_result(data['gift_name'], int(data['gift_num']))
    printer.info([f'参与了房间{real_roomid:^9}的道具抽奖'], True)
    # printer.info([f'# 道具抽奖状态: {json_response2["msg"]}'])
    printer.info([f'# 房间{real_roomid:^9}网页端活动抽奖结果: {data["gift_name"]}X{data["gift_num"]}'])
    return True
 
    
async def handle_1_guard_raffle(num, roomid, raffleid):
    await asyncio.sleep(random.uniform(0.5, min(30, num * 1.3)))
    json_response2 = await bilibili.get_gift_of_guard(roomid, raffleid)
    # print(json_response2)
    if not json_response2['code']:
        print("# 获取到房间 %s 的提督/舰长奖励: " % (roomid), json_response2['data']['message'])
        # print(json_response2)
        Statistics.append_to_guardlist()
    else:
        print(json_response2)
    return True
    
async def handle_1_storm_raffle(id):
    json_response1 = await bilibili.get_gift_of_storm(id)
    print(json_response1)
 
                                       
async def handle_1_activity_raffle(num, text1, raffleid):
    # print('参与')
    # await asyncio.sleep(random.uniform(0.5, min(30, num * 1.3)))
    json_response1 = await bilibili.get_gift_of_events_app(text1, raffleid)
    # json_pc_response = await bilibili.get_gift_of_events_web(text1, text2, raffleid)
    # print(json_response1)
    printer.info([f'参与了房间{text1:^9}的活动抽奖'], True)

    if not json_response1['code']:
        printer.info([f'# 移动端活动抽奖结果: {json_response1["data"]["gift_desc"]}'])
        Statistics.add_to_result(*(json_response1['data']['gift_desc'].split('X')))
    elif json_response1['code'] == 400:
        print(json_response1)
        return
        tasklist = []
        for i in range(60):
            task = asyncio.ensure_future(handle_1_activity_raffle_black(num, text1, raffleid))
            tasklist.append(task)
        await asyncio.wait(tasklist, return_when=asyncio.FIRST_COMPLETED)
        return
        # print(json_response1)
    else:
        printer.info([f'# 移动端活动抽奖结果: {json_response1}'])
        
    # printer.info(
    # [f'# 网页端活动抽奖状态:  {json_pc_response}'])
    # if not json_pc_response['code']:
    #    Statistics.append_to_activitylist(raffleid, text1)
    # else:
    #    print(json_pc_response)
    return True

                
async def handle_1_room_TV(real_roomid):
    result = await utils.enter_room(real_roomid)
    if result:
        json_response = await bilibili.get_giftlist_of_TV(real_roomid)
        current_time = CurrentTime()
        # print(json_response['data']['list'])
        checklen = json_response['data']['list']
        list_available_raffleid = []
        for j in checklen:
            raffle_id = j['raffleId']
            raffle_type = j['type']
            time_wanted = j['time_wait'] + current_time
            # 处理一些重复
            if not Rafflehandler().check_duplicate(raffle_id):
                print(raffle_id)
                list_available_raffleid.append((raffle_id, raffle_type, time_wanted))
                Rafflehandler().add2raffle_id(raffle_id)
            
        num_available = len(list_available_raffleid)
        # print(list_available_raffleid)
        for raffle_id, raffle_type, time_wanted in list_available_raffleid:
            BiliTimer.append2list_jobs(handle_1_TV_raffle, time_wanted, (num_available, real_roomid, raffle_id, raffle_type))
            
async def handle_1_room_storm(roomid):
    result = await utils.enter_room(roomid)
    if result:
        temp = await bilibili.get_giftlist_of_storm(roomid)
        check = len(temp['data'])
        list_available_raffleid = []
        if check != 0 and temp['data']['hasJoin'] != 1:
            id = temp['data']['id']
            list_available_raffleid.append((id, 0))
        for id, time_wanted in list_available_raffleid:
            BiliTimer.append2list_jobs(handle_1_storm_raffle, time_wanted, (id,))

async def handle_1_room_activity(text1):
    result = await utils.enter_room(text1)
    if result:
        json_response = await bilibili.get_giftlist_of_events(text1)
        # print(json_response)
        checklen = json_response['data']['lotteryInfo']
        list_available_raffleid = []
        for j in checklen:
            # await asyncio.sleep(random.uniform(0.5, 1))
            # resttime = j['time']
            raffleid = j['eventType']
            # if Statistics.check_activitylist(text1, raffleid):
            list_available_raffleid.append(raffleid)
        tasklist = []
        num_available = len(list_available_raffleid)
        # print(list_available_raffleid)
        for raffleid in list_available_raffleid:
            task = asyncio.ensure_future(handle_1_activity_raffle(num_available, text1, raffleid))
            tasklist.append(task)
        if tasklist:
            raffle_results = await asyncio.gather(*tasklist)
            if False in raffle_results:
                print('有繁忙提示，稍后重新尝试')
                Rafflehandler.Put2Queue((text1), handle_1_room_activity)

                
async def handle_1_room_guard(roomid):
    result = await utils.enter_room(roomid)
    if result:
        for i in range(10):
            json_response1 = await bilibili.get_giftlist_of_guard(roomid)
            # print(json_response1)
            if not json_response1['data']:
                await asyncio.sleep(1)
            else:
                break
        if not json_response1['data']:
            print(f'{roomid}没有guard或者guard已经领取')
            return
        list_available_raffleid = []
        # guard这里领取后，list对应会消失，其实就没有status了，这里是为了统一
        for j in json_response1['data']:
            id = j['id']
            status = j['status']
            if status == 1:
                # print('未参加')
                list_available_raffleid.append(id)
            elif status == 2:
                # print('过滤')
                pass
            else:
                print(json_response1)
            
        tasklist = []
        num_available = len(list_available_raffleid)
        for raffleid in list_available_raffleid:
            task = asyncio.ensure_future(handle_1_guard_raffle(num_available, roomid, raffleid))
            tasklist.append(task)
        if tasklist:
            raffle_results = await asyncio.gather(*tasklist)
            if False in raffle_results:
                print('有繁忙提示，稍后重新尝试')
                Rafflehandler.Put2Queue((roomid,), handle_1_room_guard)
                
         
async def handle_1_TV_raffle_black(num, real_roomid, raffleid, raffle_type):
    # print('ffffffffffggggdgdfddf')
    for i in range(50):
        json_response2 = await bilibili.get_gift_of_TV_app(real_roomid, raffleid, raffle_type)
        code = json_response2['code']
        if not code:
            break
        elif code == -403:
            return True
        elif code == -405:
            print('没抢到。。。。。')
            printer.warn(raffleid)
            return False
        elif code != -401 and code != -403:
            # print('00', json_response2)
            pass
        # await asyncio.sleep()
    code = json_response2['code']
    if code:
        await asyncio.sleep(5)
        return
    data = json_response2['data']
    Statistics.append_to_TVlist(raffleid, real_roomid)
    Statistics.add_to_result(data['gift_name'], int(data['gift_num']))
    printer.info([f'参与了房间{real_roomid:^9}的道具抽奖'], True)
    # printer.info([f'# 道具抽奖状态: {json_response2["msg"]}'])
    printer.info([f'# 房间{real_roomid:^9}网页端活动抽奖结果: {data["gift_name"]}X{data["gift_num"]}'])
    return True
    
async def handle_1_activity_raffle_black(num, text1, raffleid):
    # print('参与')
    # await asyncio.sleep(random.uniform(0.5, min(30, num * 1.3)))
    for i in range(50):
        json_response1 = await bilibili.get_gift_of_events_app(text1, raffleid)
        code = json_response1['code']
        if not code:
            break
        elif code == -403:
            return True
        elif code == -405:
            print('没抢到。。。。。')
            printer.warn(raffleid)
            return False
        elif code != -401 and code != -403:
            # print('00', json_response2)
            pass
    # json_pc_response = await bilibili.get_gift_of_events_web(text1, text2, raffleid)
    # print(json_response1)
    printer.info([f'参与了房间{text1:^9}的活动抽奖'], True)

    if not json_response1['code']:
        printer.info([f'# 移动端活动抽奖结果: {json_response1["data"]["gift_desc"]}'])
        Statistics.add_to_result(*(json_response1['data']['gift_desc'].split('X')))
    else:
        # print(json_response1)
        printer.info([f'# 移动端活动抽奖结果: {json_response1}'])

    return True
