import utils
from statistics import Statistics
from connect import connect
from printer import Printer
from configloader import ConfigLoader
from rafflehandler import Rafflehandler
import rafflehandler
import OnlineHeart
import asyncio
from cmd import Cmd
    

def fetch_real_roomid(roomid):
    if roomid:
        real_roomid = [[roomid], utils.check_room]
    else:
        real_roomid = ConfigLoader().dic_user['other_control']['default_monitor_roomid']
    return real_roomid
  
              
class Biliconsole(Cmd):
    prompt = ''

    def __init__(self, loop):
        self.loop = loop
        Cmd.__init__(self)
        
    def guide_of_console(self):
        print('___________________________')
        print('| 欢迎使用本控制台           |')
        print('|1 输出本次抽奖统计          |')
        print('|2 查看目前拥有礼物的统计     |')
        print('|3 查看持有勋章状态          |')
        print('|4 获取直播个人的基本信息     |')
        print('|5 检查今日任务的完成情况     |')
        print('|6 模拟电脑网页端发送弹幕     |')
        print('|7 直播间的长短号码的转化     |')
        print('|8 手动送礼物到指定直播间     |')
        print('|9 切换监听的直播间          |')
        print('|10 T或F控制弹幕的开关       |')
        print('|11 房间号码查看主播         |')
        print('|12 当前拥有的扭蛋币         |')
        print('|13 开扭蛋币(只能1，10，100) |')
        print('|16 尝试一次实物抽奖         |')
        print('￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣')
        
    def default(self, line):
        self.guide_of_console()
        
    def emptyline(self):
        self.guide_of_console()
        
    def do_1(self, line):
        Statistics.getlist()
        Statistics.getresult()
        
    def do_2(self, line):
        self.append2list_console(utils.fetch_bag_list)
        
    def do_3(self, line):
        self.append2list_console(utils.fetch_medal)
        
    def do_4(self, line):
        self.append2list_console(utils.fetch_user_info)
        
    def do_5(self, line):
        self.append2list_console(utils.check_taskinfo)
        
    def do_6(self, line):
        msg = input('请输入要发送的信息:')
        roomid = input('请输入要发送的房间号:')
        real_roomid = fetch_real_roomid(roomid)
        self.append2list_console([[msg, real_roomid], utils.send_danmu_msg_web])
        
    def do_7(self, line):
        roomid = input('请输入要转化的房间号:')
        if not roomid:
            roomid = ConfigLoader().dic_user['other_control']['default_monitor_roomid']
        self.append2list_console([[roomid], utils.check_room])
    
    def do_8(self, line):
        self.append2list_console([[True], utils.fetch_bag_list])
        bagid = input('请输入要发送的礼物编号:')
        # print('是谁', giftid)
        giftnum = int(input('请输入要发送的礼物数目:'))
        roomid = input('请输入要发送的房间号:')
        real_roomid = fetch_real_roomid(roomid)
        self.append2list_console([[real_roomid, giftnum, bagid], utils.send_gift_web])
    
    def do_9(self, line):
        roomid = input('请输入roomid')
        real_roomid = fetch_real_roomid(roomid)
        self.append2list_console([[real_roomid], connect.reconnect])
        
    def do_10(self, line):
        new_words = input('弹幕控制')
        if new_words == 'T':
            Printer().dic_user['print_control']['danmu'] = True
        else:
            Printer().dic_user['print_control']['danmu'] = False
            
    def do_11(self, line):
        roomid = input('请输入roomid')
        real_roomid = fetch_real_roomid(roomid)
        self.append2list_console([[real_roomid], utils.fetch_liveuser_info])
    
    def do_12(self, line):
        self.append2list_console(utils.fetch_capsule_info)
        
    def do_13(self, line):
        count = input('请输入要开的扭蛋数目(1或10或100)')
        self.append2list_console([[count], utils.open_capsule])
        
    def do_14(self, line):
        if ConfigLoader().dic_user['platform']['platform'] == 'ios_pythonista':
            roomid = input('请输入roomid')
            real_roomid = fetch_real_roomid(roomid)
            self.append2list_console([[real_roomid], utils.watch_living_video])
            return
        print('仅支持ios')
        
    def do_15(self, line):
        self.append2list_console(utils.TitleInfo)
        
    def do_16(self, line):
        self.append2list_console(OnlineHeart.draw_lottery)
        
    def do_17(self, line):
        new_words = input('debug控制')
        if new_words == 'T':
            Printer().dic_user['print_control']['debug'] = True
        else:
            Printer().dic_user['print_control']['debug'] = False
            
    def do_18(self, line):
        video_id = input('请输入av号')
        num = input('输入数目')
        self.append2list_console([[int(video_id), int(num)], utils.GiveCoin2Av])
        
    def do_19(self, line):
        try:
            roomid = int(input('输入roomid'))
            self.append2list_console([[(roomid,), rafflehandler.handle_1_room_guard], rafflehandler.Rafflehandler.Put2Queue_wait])
        except:
            pass
        
    def do_check(self, line):
        Rafflehandler.getlist()
        Statistics.checklist()
        
    def append2list_console(self, request):
        asyncio.run_coroutine_threadsafe(self.excute_async(request), self.loop)
        # inst.loop.call_soon_threadsafe(inst.queue_console.put_nowait, request)
        
    async def excute_async(self, i):
        if isinstance(i, list):
            # 对10号单独简陋处理
            for j in range(len(i[0])):
                if isinstance(i[0][j], list):
                    # print('检测')
                    i[0][j] = await i[0][j][1](*(i[0][j][0]))
            if i[1] == 'normal':
                i[2](*i[0])
            else:
                await i[1](*i[0])
        else:
            await i()
    
    
    
