from bilibili import bilibili
from printer import Printer
import time
import datetime
from PIL import Image
from io import BytesIO
import webbrowser
import re


def adjust_for_chinese(str):
    SPACE = '\N{IDEOGRAPHIC SPACE}'
    EXCLA = '\N{FULLWIDTH EXCLAMATION MARK}'
    TILDE = '\N{FULLWIDTH TILDE}'

    # strings of ASCII and full-width characters (same order)
    west = ''.join(chr(i) for i in range(ord(' '), ord('~')))
    east = SPACE + ''.join(chr(i) for i in range(ord(EXCLA), ord(TILDE)))

    # build the translation table
    full = str.maketrans(west, east)
    str = str.translate(full).rstrip().split('\n')
    md = '{:^10}'.format(str[0])
    return md.translate(full)


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return str(currenttime)
    
    
def seconds_until_tomorrow():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_start_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d')))
    current_time = int(time.mktime(datetime.datetime.now().timetuple()))
    return tomorrow_start_time - current_time


async def fetch_medal(printer=True):
    printlist = []
    if printer:
        printlist.append('查询勋章信息')
        printlist.append('{} {} {:^12} {:^10} {} {:^6} '.format(adjust_for_chinese('勋章'), adjust_for_chinese('主播昵称'), '亲密度', '今日的亲密度',
                                                 adjust_for_chinese('排名'), '勋章状态'))
    dic_worn = {'1': '正在佩戴', '0': '待机状态'}
    response = await bilibili().request_fetchmedal()
    # print(response.json())
    json_response = await response.json()
    roomid = 0
    today_feed = 0
    day_limit = 0
    if json_response['code'] == 0:
        for i in json_response['data']['fansMedalList']:
            if i['status'] == 1:
                roomid = i['roomid']
                today_feed = i['today_feed']
                day_limit = i['day_limit']
            if printer:
                printlist.append('{} {} {:^14} {:^14} {} {:^6} '.format(adjust_for_chinese(i['medal_name'] + '|' + str(i['level'])),
                                                           adjust_for_chinese(i['anchorInfo']['uname']),
                                                           str(i['intimacy']) + '/' + str(i['next_intimacy']),
                                                           str(i['todayFeed']) + '/' + str(i['dayLimit']),
                                                           adjust_for_chinese(str(i['rank'])),
                                                           dic_worn[str(i['status'])]))
        if printer:
            Printer().printlist_append(['join_lottery', '', 'user', printlist], True)
        return roomid, today_feed, day_limit
        
        
async def send_danmu_msg_andriod(msg, roomId):
    response = await bilibili().request_send_danmu_msg_andriod(msg, roomId)
    # print('ggghhhjj')
    print(await response.json())

async def send_danmu_msg_web(msg, roomId):
    response = await bilibili().request_send_danmu_msg_web(msg, roomId)
    print(await response.json())
    
        
def find_live_user_roomid(wanted_name):
    print('期望名字', wanted_name)
    for i in range(len(wanted_name), 0, -1):
        response = bilibili().request_search_user(wanted_name[:i])
        results = response.json()['result']
        if results is None:
            print('屏蔽全名')
            continue
        for i in results:
            real_name = re.sub(r'<[^>]*>', '', i['uname'])
            # print('去除干扰', real_name)
            if real_name == wanted_name:
                print('找到结果', i['room_id'])
                return i['room_id']
        print('结束一次')

    
async def fetch_capsule_info():
    response = await bilibili().request_fetch_capsule()
    json_response = await response.json()
    # print(json_response)
    if (json_response['code'] == 0):
        data = json_response['data']
        if data['colorful']['status']:
            print('梦幻扭蛋币: {}个'.format(data['colorful']['coin']))
        else:
            print('梦幻扭蛋币暂不可用')
            
        data = json_response['data']
        if data['normal']['status']:
            print('普通扭蛋币: {}个'.format(data['normal']['coin']))
        else:
            print('普通扭蛋币暂不可用')
            
async def open_capsule(count):
    response = await bilibili().request_open_capsule(count)
    json_response = await response.json()
    # print(json_response)
    if (json_response['code'] == 0):
        # print(json_response['data']['text'])
        for i in json_response['data']['text']:
            print(i)
            
async def watch_living_video(cid):
    import sound
    sound.set_honors_silent_switch(False)
    sound.set_volume(1)
    sound.play_effect('piano:D3')
    response = await bilibili().request_playurl(cid)
    json_response = await response.json(content_type=None)
    print(json_response)
    if (json_response['code'] == 0):
        data = json_response['data']
        print(data)
        webbrowser.open(data)
        

async def fetch_user_info():
    response = await bilibili().request_fetch_user_info()
    response_ios = await bilibili().request_fetch_user_infor_ios()
    print('[{}] 查询用户信息'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    json_response = await response.json()
    json_response_ios = await response_ios.json()
    if json_response_ios['code'] == 0:
        gold_ios = json_response_ios['data']['gold']
    # print(json_response_ios)
    if (json_response['code'] == 0):
        data = json_response['data']
        # print(data)
        userInfo = data['userInfo']
        userCoinIfo = data['userCoinIfo']
        uname = userInfo['uname']
        achieve = data['achieves']
        user_level = userCoinIfo['user_level']
        silver = userCoinIfo['silver']
        gold = userCoinIfo['gold']
        identification = bool(userInfo['identification'])
        mobile_verify = bool(userInfo['mobile_verify'])
        user_next_level = userCoinIfo['user_next_level']
        user_intimacy = userCoinIfo['user_intimacy']
        user_next_intimacy = userCoinIfo['user_next_intimacy']
        user_level_rank = userCoinIfo['user_level_rank']
        billCoin = userCoinIfo['coins']
        bili_coins = userCoinIfo['bili_coins']
        print('# 用户名', uname)
        size = 100, 100
        response_face = bilibili().request_load_img(userInfo['face'])
        img = Image.open(BytesIO(response_face.content))
        img.thumbnail(size)
        try:
            img.show()
        except:
            pass
        print('# 手机认证状况 {} | 实名认证状况 {}'.format(mobile_verify, identification))
        print('# 银瓜子', silver)
        print('# 通用金瓜子', gold)
        print('# ios可用金瓜子', gold_ios)
        print('# 硬币数', billCoin)
        print('# b币数', bili_coins)
        print('# 成就值', achieve)
        print('# 等级值', user_level, '———>', user_next_level)
        print('# 经验值', user_intimacy)
        print('# 剩余值', user_next_intimacy - user_intimacy)
        arrow = int(user_intimacy * 30 / user_next_intimacy)
        line = 30 - arrow
        percent = user_intimacy / user_next_intimacy * 100.0
        process_bar = '# [' + '>' * arrow + '-' * line + ']' + '%.2f' % percent + '%'
        print(process_bar)
        print('# 等级榜', user_level_rank)

async def fetch_bag_list(verbose=False, bagid=None, printer=True):
    response = await bilibili().request_fetch_bag_list()
    temp = []
    gift_list = []
    json_response = await response.json()
    # print(json_response)
    if printer:
        print('[{}] 查询可用礼物'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    for i in range(len(json_response['data']['list'])):
        bag_id = (json_response['data']['list'][i]['bag_id'])
        gift_id = (json_response['data']['list'][i]['gift_id'])
        gift_num = str((json_response['data']['list'][i]['gift_num'])).center(4)
        gift_name = json_response['data']['list'][i]['gift_name']
        expireat = (json_response['data']['list'][i]['expire_at'])
        left_time = (expireat - json_response['data']['time'])
        if expireat == 0:
            left_days = '+∞'.center(6)
        else:
            left_days = str(round(left_time / 86400, 1)).center(6)
        gift_list.append([gift_id, gift_num, bag_id])
        if bagid is not None:
            if bag_id == int(bagid):
                return gift_id
        else:
            if verbose:
                print("# 编号为" + str(bag_id) + '的'+ gift_name.center(3) + 'X' + gift_num, '(在' + left_days + '天后过期)')
            elif printer:
                print("# " + gift_name.center(3) + 'X' + gift_num, '(在' + left_days + '天后过期)')

        if 0 < int(left_time) < 43200:   # 剩余时间少于半天时自动送礼
            temp.append([gift_id, gift_num, bag_id])
    # print(temp)
    return temp, gift_list
    
async def check_taskinfo():
    response = await bilibili().request_check_taskinfo()
    json_response = await response.json()
    # print(json_response)
    if json_response['code'] == 0:
        data = json_response['data']
        double_watch_info = data['double_watch_info']
        box_info = data['box_info']
        sign_info = data['sign_info']
        live_time_info = data['live_time_info']
        print('双端观看直播：')
        if double_watch_info['status'] == 1:
            print('# 该任务已完成，但未领取奖励')
        elif double_watch_info['status'] == 2:
            print('# 该任务已完成，已经领取奖励')
        else:
            print('# 该任务未完成')
            if double_watch_info['web_watch'] == 1:
                print('## 网页端观看任务已完成')
            else:
                print('## 网页端观看任务未完成')
            
            if double_watch_info['mobile_watch'] == 1:
                print('## 移动端观看任务已完成')
            else:
                print('## 移动端观看任务未完成')
                
        print('直播在线宝箱：')
        if box_info['status'] == 1:
            print('# 该任务已完成')
        else:
            print('# 该任务未完成')
            print('## 一共{}次重置次数，当前为第{}次第{}个礼包(每次3个礼包)'.format(box_info['max_times'], box_info['freeSilverTimes'], box_info['type']))
            
        print('每日签到：')
        if sign_info['status'] == 1:
            print('# 该任务已完成')
        else:
            print('# 该任务未完成')
            
        if sign_info['signDaysList'] == list(range(1, sign_info['curDay'] + 1)):
            print('# 当前全勤')
        else:
            print('# 出现断签')
        
        print('直播奖励：')
        if live_time_info['status'] == 1:
            print('# 已完成')
        else:
            print('# 未完成(目前本项目未实现自动完成直播任务)')
            
async def check_room(roomid):
    response = await bilibili().request_check_room(roomid)
    json_response = await response.json(content_type=None)
    if json_response['code'] == 0:
        # print(json_response)
        print('查询结果:')
        data = json_response['data']
        
        if data['short_id'] == 0:
            print('# 此房间无短房号')
        else:
            print('# 短号为:{}'.format(data['short_id']))
        print('# 真实房间号为:{}'.format(data['room_id']))
        return data['room_id']
            
            
async def send_gift_web(roomid, giftid, giftnum, bagid):
    response = await bilibili().request_check_room(roomid)
    json_response = await response.json()
    ruid = json_response['data']['uid']
    biz_id = json_response['data']['room_id']
    response1 = await bilibili().request_send_gift_web(giftid, giftnum, bagid, ruid, biz_id)
    json_response1 = await response1.json()
    if json_response1['code'] == 0:
        # print(json_response1['data'])
        print("# 送出礼物:", json_response1['data']['gift_name'] + "X" + str(json_response1['data']['gift_num']))
    else:
        print("# 错误", json_response1['msg'])
 
        
async def fetch_liveuser_info(real_roomid):
    response = await bilibili().request_fetch_liveuser_info(real_roomid)
    json_response = await response.json(content_type=None)
    if json_response['code'] == 0:
        data = json_response['data']
        # print(data)
        print('# 主播姓名 {}'.format(data['info']['uname']))
        
        uid = data['level']['uid']  # str
        response_fan = await bilibili().request_fetch_fan(real_roomid, uid)
        json_response_fan = await response_fan.json(content_type=None)
        # print(json_response_fan)
        data_fan = json_response_fan['data']
        if json_response_fan['code'] == 0 and data_fan['medal']['status'] == 2:
            print('# 勋章名字: {}'.format(data_fan['list'][0]['medal_name']))
        else:
            print('# 该主播暂时没有开通勋章')
            # print(json_response_fan)

        size = 100, 100
        response_face = bilibili().request_load_img(data['info']['face'])
        img = Image.open(BytesIO(response_face.content))
        img.thumbnail(size)
        try:
            img.show()
        except:
            pass


async def check_room_true(roomid):
    response = await bilibili().request_check_room(roomid)
    json_response = await response.json(content_type=None)
    
    if json_response['code'] == 0:
        data = json_response['data']
        param1 = data['is_hidden']
        param2 = data['is_locked']
        param3 = data['encrypted']
        # print(param1, param2, param3)
        return param1, param2, param3
    

