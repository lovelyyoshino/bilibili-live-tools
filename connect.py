import asyncio
import utils
import bilibiliCilent
import printer
from bilibili import bilibili
from configloader import ConfigLoader
import random

     
async def check_room_state(roomid):
    json_rsp = await bilibili.req_room_init(roomid)
    return json_rsp['data']['live_status']

async def get_one(areaid):
    # 1 娱乐分区, 2 游戏分区, 3 手游分区, 4 绘画分区
    if areaid == 1:
        roomid = 23058
        state = await check_room_state(roomid)
        if state == 1:
            printer.info([f'{areaid}号弹幕监控选择房间（{roomid}）'], True)
            return roomid
            
    while True:
        json_rsp = await bilibili.req_realroomid(areaid)
        data = json_rsp['data']
        roomid = random.choice(data)['roomid']
        state = await check_room_state(roomid)
        if state == 1:
            printer.info([f'{areaid}号弹幕监控选择房间（{roomid}）'], True)
            return roomid


class connect():
    __slots__ = ('danmuji')
    instance = None
    
    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(connect, cls).__new__(cls, *args, **kw)
            cls.instance.danmuji = None
        return cls.instance
        
    async def run(self):
        self.danmuji = bilibiliCilent.DanmuPrinter()
        while True:
            print('# 正在启动直播监控弹幕姬')
            time_start = int(utils.CurrentTime())
            connect_results = await self.danmuji.connectServer()
            # print(connect_results)
            if not connect_results:
                continue
            task_main = asyncio.ensure_future(self.danmuji.ReceiveMessageLoop())
            task_heartbeat = asyncio.ensure_future(self.danmuji.HeartbeatLoop())
            finished, pending = await asyncio.wait([task_main, task_heartbeat], return_when=asyncio.FIRST_COMPLETED)
            print('主弹幕姬异常或主动断开，正在处理剩余信息')
            time_end = int(utils.CurrentTime())
            if not task_heartbeat.done():
                task_heartbeat.cancel()
            task_terminate = asyncio.ensure_future(self.danmuji.close_connection())
            await asyncio.wait(pending)
            await asyncio.wait([task_terminate])
            printer.info(['主弹幕姬退出，剩余任务处理完毕'], True)
            if time_end - time_start < 5:
                print('# 当前网络不稳定，为避免频繁不必要尝试，将自动在5秒后重试')
                await asyncio.sleep(5)
    
    @staticmethod
    async def reconnect(roomid):
        ConfigLoader().dic_user['other_control']['default_monitor_roomid'] = roomid
        print('已经切换roomid')
        if connect.instance.danmuji is not None:
            connect.instance.danmuji.roomid = roomid
            await connect.instance.danmuji.close_connection()
        
        
class RaffleConnect():
    def __init__(self, areaid):
        self.danmuji = None
        self.roomid = 0
        self.areaid = areaid
        
    async def run(self):
        self.danmuji = bilibiliCilent.DanmuRaffleHandler(self.roomid, self.areaid)
        while True:
            self.danmuji.roomid = await get_one(self.areaid)
            printer.info(['# 正在启动抽奖监控弹幕姬'], True)
            time_start = int(utils.CurrentTime())
            connect_results = await self.danmuji.connectServer()
            # print(connect_results)
            if not connect_results:
                continue
            task_main = asyncio.ensure_future(self.danmuji.ReceiveMessageLoop())
            task_heartbeat = asyncio.ensure_future(self.danmuji.HeartbeatLoop())
            task_checkarea = asyncio.ensure_future(self.danmuji.CheckArea())
            finished, pending = await asyncio.wait([task_main, task_heartbeat, task_checkarea], return_when=asyncio.FIRST_COMPLETED)
            printer.info([f'{self.areaid}号弹幕姬异常或主动断开，正在处理剩余信息'], True)
            time_end = int(utils.CurrentTime())
            if not task_heartbeat.done():
                task_heartbeat.cancel()
            if not task_checkarea.done():
                task_checkarea.cancel()
            task_terminate = asyncio.ensure_future(self.danmuji.close_connection())
            await asyncio.wait(pending)
            await asyncio.wait([task_terminate])
            printer.info([f'{self.areaid}号弹幕姬退出，剩余任务处理完毕'], True)
            if time_end - time_start < 5:
                print('# 当前网络不稳定，为避免频繁不必要尝试，将自动在5秒后重试')
                await asyncio.sleep(5)
                
                
class YjConnection():
    def __init__(self):
        self.danmuji = None
        self.roomid = 0
        self.areaid = -1
        
    async def run(self):
        self.roomid = ConfigLoader().dic_user['other_control']['raffle_minitor_roomid']
        if not self.roomid:
            print('hjjkkk结束了坎坎坷坷坎坎坷坷')
            return
        self.danmuji = bilibiliCilent.YjMonitorHandler(self.roomid, self.areaid)
        while True:
            print('# 正在启动直播监控弹幕姬')
            time_start = int(utils.CurrentTime())
            connect_results = await self.danmuji.connectServer()
            # print(connect_results)
            if not connect_results:
                continue
            task_main = asyncio.ensure_future(self.danmuji.ReceiveMessageLoop())
            task_heartbeat = asyncio.ensure_future(self.danmuji.HeartbeatLoop())
            finished, pending = await asyncio.wait([task_main, task_heartbeat], return_when=asyncio.FIRST_COMPLETED)
            print('主弹幕姬异常或主动断开，正在处理剩余信息')
            time_end = int(utils.CurrentTime())
            if not task_heartbeat.done():
                task_heartbeat.cancel()
            task_terminate = asyncio.ensure_future(self.danmuji.close_connection())
            await asyncio.wait(pending)
            await asyncio.wait([task_terminate])
            printer.info(['主弹幕姬退出，剩余任务处理完毕'], True)
            if time_end - time_start < 5:
                print('# 当前网络不稳定，为避免频繁不必要尝试，将自动在5秒后重试')
                await asyncio.sleep(5)
            
            

        
                    
