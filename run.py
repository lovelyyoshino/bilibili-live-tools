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
queue = asyncio.Queue()
fileDir = os.path.dirname(os.path.realpath('__file__'))
file_color = f'{fileDir}/conf/color.toml'
file_user = f'{fileDir}/conf/user.toml'
file_bilibili = f'{fileDir}/conf/bilibili.toml'
ConfigLoader(colorfile=file_color, userfile=file_user, bilibilifile=file_bilibili)

# print('Hello world.')
printer = Printer()
bilibili()
login.login()
Statistics()

rafflehandler = Rafflehandler()
biliconsole.Biliconsole(loop, queue)

danmu_connection = connect()


bili_timer = BiliTimer()


console_thread = threading.Thread(target=biliconsole.controler)

console_thread.start()

tasks = [
    OnlineHeart.run(),
    Silver.run(),
    danmu_connection.run(),
    LotteryResult.run(),
    rafflehandler.run(),
    biliconsole.Biliconsole.run(),
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
    


