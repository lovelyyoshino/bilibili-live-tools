import OnlineHeart
import Silver
import LotteryResult
import Tasks
from connect import connect
from rafflehandler import Rafflehandler
import asyncio
from printer import Printer
from statistics import Statistics
from bilibili import bilibili
from configloader import ConfigLoader
import threading
import os
import login
import biliconsole
from bilitimer import BiliTimer


loop = asyncio.get_event_loop()
fileDir = os.path.dirname(os.path.realpath('__file__'))
file_color = f'{fileDir}/conf/color.conf'
file_user = f'{fileDir}/conf/user.conf'
file_bilibili = f'{fileDir}/conf/bilibili.conf'
ConfigLoader(colorfile=file_color, userfile=file_user, bilibilifile=file_bilibili)

# print('Hello world.')
printer = Printer()
bilibili()
login.login()
Statistics()

rafflehandler = Rafflehandler()
biliconsole.Biliconsole()

danmu_connection = connect()


bili_timer = BiliTimer()
OnlineHeart.init()
Tasks.init()
Silver.init()


console_thread = threading.Thread(target=biliconsole.controler)

console_thread.start()

loop = asyncio.get_event_loop()
tasks = [
    # utils.fetch_user_info(),
    # utils.fetch_bag_list(),
    # utils.fetch_medal(),
    
    # OnlineHeart.run(),
    # Silver.run(),
    # Tasks.run(),
    danmu_connection.run(),
    LotteryResult.run(),
    rafflehandler.run(),
    biliconsole.Biliconsole().run(),
    bili_timer.run()
    
]
try:
    loop.run_until_complete(asyncio.wait(tasks))
except KeyboardInterrupt:
    # print(sys.exc_info()[0], sys.exc_info()[1])
    if ConfigLoader().dic_user['other_control']['keep-login']:
        pass
    else:
        response = login.logout()
    
console_thread.join()

loop.close()
    


