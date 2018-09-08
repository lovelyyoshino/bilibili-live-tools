from bilibili import bilibili
from statistics import Statistics
import printer
from printer import Printer
import rafflehandler
from configloader import ConfigLoader
import utils
import asyncio
import struct
import json
import sys
import aiohttp
                                                          

class BaseDanmu():
    
    __slots__ = ('ws', 'roomid', 'area_id', 'client')
    structer = struct.Struct('!I2H2I')

    def __init__(self, roomid=None, area_id=None):
        self.client = aiohttp.ClientSession()
        if roomid is None:
            self.roomid = ConfigLoader().dic_user['other_control']['default_monitor_roomid']
            self.area_id = 0
        else:
            self.roomid = roomid
            self.area_id = area_id

    # 待确认
    async def close_connection(self):
        try:
            await self.ws.close()
        except:
            print('请联系开发者', sys.exc_info()[0], sys.exc_info()[1])
        printer.info([f'{self.area_id}号弹幕收尾模块状态{self.ws.closed}'], True)
        
    async def CheckArea(self):
        try:
            while True:
                area_id = await asyncio.shield(utils.FetchRoomArea(self.roomid))
                if area_id != self.area_id:
                    printer.info([f'{self.roomid}更换分区{self.area_id}为{area_id}，即将切换房间'], True)
                    return
                await asyncio.sleep(300)
        except asyncio.CancelledError:
            printer.info([f'{self.area_id}号弹幕监控分区检测模块主动取消'], True)
        
    async def connectServer(self):
        try:
            url = 'wss://broadcastlv.chat.bilibili.com:443/sub'
            
            self.ws = await asyncio.wait_for(self.client.ws_connect(url), timeout=3)
        except:
            print("# 连接无法建立，请检查本地网络状况")
            print(sys.exc_info()[0], sys.exc_info()[1])
            return False
        printer.info([f'{self.area_id}号弹幕监控已连接b站服务器'], True)
        body = f'{{"uid":0,"roomid":{self.roomid},"protover":1,"platform":"web","clientver":"1.3.3"}}'
        return (await self.SendSocketData(opt=7, body=body))

    async def HeartbeatLoop(self):
        printer.info([f'{self.area_id}号弹幕监控开始心跳（心跳间隔30s，后续不再提示）'], True)
        try:
            while True:
                if not (await self.SendSocketData(opt=2, body='')):
                    return
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            printer.info([f'{self.area_id}号弹幕监控心跳模块主动取消'], True)

    async def SendSocketData(self, opt, body, len_header=16, ver=1, seq=1):
        remain_data = body.encode('utf-8')
        len_data = len(remain_data) + len_header
        header = self.structer.pack(len_data, len_header, ver, opt, seq)
        data = header + remain_data
        try:
            await self.ws.send_bytes(data)
        except asyncio.CancelledError:
            printer.info([f'{self.area_id}号弹幕监控发送模块主动取消'], True)
            return False
        except:
            print(sys.exc_info()[0], sys.exc_info()[1])
            return False
        return True

    async def ReadSocketData(self):
        bytes_data = None
        try:
            msg = await asyncio.wait_for(self.ws.receive(), timeout=35.0)
            bytes_data = msg.data
        except asyncio.TimeoutError:
            print('# 由于心跳包30s一次，但是发现35内没有收到任何包，说明已经悄悄失联了，主动断开')
            return None
        except:
            print(sys.exc_info()[0], sys.exc_info()[1])
            print('请联系开发者')
            return None
        
        return bytes_data
    
    async def ReceiveMessageLoop(self):
        while True:
            bytes_datas = await self.ReadSocketData()
            if bytes_datas is None:
                break
            len_read = 0
            len_bytes_datas = len(bytes_datas)
            loop_time = 0
            while len_read != len_bytes_datas:
                loop_time += 1
                if loop_time > 100:
                    print('请联系作者', bytes_datas)
                state = None
                split_header = self.structer.unpack(bytes_datas[len_read:16+len_read])
                len_data, len_header, ver, opt, seq = split_header
                remain_data = bytes_datas[len_read+16:len_read+len_data]
                # 人气值/心跳 3s间隔
                if opt == 3:
                    # self._UserCount, = struct.unpack('!I', remain_data)
                    printer.debug(f'弹幕心跳检测{self.area_id}')
                # cmd
                elif opt == 5:
                    messages = remain_data.decode('utf-8')
                    dic = json.loads(messages)
                    state = self.handle_danmu(dic)
                # 握手确认
                elif opt == 8:
                    printer.info([f'{self.area_id}号弹幕监控进入房间（{self.roomid}）'], True)
                else:
                    printer.warn(bytes_datas[len_read:len_read + len_data])
                            
                if state is not None and not state:
                    return
                len_read += len_data
                
    def handle_danmu(self, dic):
        return True
                
                
class DanmuPrinter(BaseDanmu):
    def handle_danmu(self, dic):
        cmd = dic['cmd']
        # print(cmd)
        if cmd == 'DANMU_MSG':
            # print(dic)
            Printer().print_danmu(dic)
            return

        
class DanmuRaffleHandler(BaseDanmu):
    def handle_danmu(self, dic):
        cmd = dic['cmd']
        
        if cmd == 'PREPARING':
            printer.info([f'{self.area_id}号弹幕监控房间下播({self.roomid})'], True)
            return False
        elif cmd == 'SYS_GIFT':
            if 'giftId' in dic:
                if dic['giftId'] == 39:
                    printer.info(["节奏风暴"], True)
                    roomid = dic['roomid']
                    rafflehandler.Rafflehandler.Put2Queue((roomid,), rafflehandler.handle_1_room_storm)
                    Statistics.append2pushed_raffle('节奏风暴', area_id=self.area_id)
                else:
                    text1 = dic['real_roomid']
                    text2 = dic['url']
                    printer.info([dic, "请联系开发者"])
                    try:
                        giftId = dic['giftId']
                        printer.info(["检测到房间{:^9}的{}活动抽奖".format(text1, bilibili.get_giftids_raffle(str(giftId)))], True)
                        rafflehandler.Rafflehandler.Put2Queue((giftId, text1, text2), rafflehandler.handle_1_room_activity)
                        Statistics.append2pushed_raffle('活动', area_id=self.area_id)
                                
                    except:
                        printer.info([dic, "请联系开发者"])
                    
            else:
                printer.info(['普通送礼提示', dic['msg_text']])
            return
        elif cmd == 'SYS_MSG':
            if 'real_roomid' in dic:
                real_roomid = dic['real_roomid']
                type_text = (dic['msg'].split(':?')[-1]).split('，')[0][2:]
                printer.info([f'{self.area_id}号弹幕监控检测到{real_roomid:^9}的{type_text}'], True)
                rafflehandler.Rafflehandler.Put2Queue((real_roomid,), rafflehandler.handle_1_room_TV)
                rafflehandler.Rafflehandler.Put2Queue((real_roomid,), rafflehandler.handle_1_room_activity)
                Statistics.append2pushed_raffle(type_text, area_id=self.area_id)
        
        elif cmd == 'GUARD_MSG':
            if 'buy_type' in dic and dic['buy_type'] == 1:
                roomid = dic['roomid']
                printer.info([f'{self.area_id}号弹幕监控检测到{roomid:^9}的总督'], True)
                rafflehandler.Rafflehandler.Put2Queue((roomid,), rafflehandler.handle_1_room_guard)
                Statistics.append2pushed_raffle('总督', area_id=self.area_id)
            if 'buy_type' in dic and dic['buy_type'] != 1:
                print(dic)
                # roomid = dic['roomid']
                printer.info([f'{self.area_id}号弹幕监控检测到{self.roomid:^9}的提督/舰长'], True)
                rafflehandler.Rafflehandler.Put2Queue((self.roomid,), rafflehandler.handle_1_room_guard)
                Statistics.append2pushed_raffle('提督/舰长', area_id=self.area_id)
            
        
class YjMonitorHandler(BaseDanmu):
    def handle_danmu(self, dic):
        cmd = dic['cmd']
        # print(cmd)
        if cmd == 'DANMU_MSG':
            msg = dic['info'][1]
            if '-' in msg:
                list_word = msg.split('-')
                try:
                    roomid = int(list_word[0])
                    raffleid = int(list_word[1])
                    printer.info([f'弹幕监控检测到{roomid:^9}的提督/舰长{raffleid}'], True)
                    rafflehandler.Rafflehandler.Put2Queue((1, roomid, raffleid), rafflehandler.handle_1_guard_raffle)
                    Statistics.append2pushed_raffle('提督/舰长', area_id=1)
                except ValueError:
                    print(msg)
            Printer().print_danmu(dic)
                    
                    
               
    
