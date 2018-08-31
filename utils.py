from bilibili import bilibili
import printer
import time
import datetime
from PIL import Image
from io import BytesIO
import webbrowser
import re
from operator import itemgetter
from configloader import ConfigLoader


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
    md = f'{str[0]:^10}'
    return md.translate(full)


def CurrentTime():
    currenttime = int(time.time())
    return str(currenttime)


def seconds_until_tomorrow():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_start_time = int(time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d')))
    current_time = int(time.mktime(datetime.datetime.now().timetuple()))
    return tomorrow_start_time - current_time

async def WearingMedalInfo():
    json_response = await bilibili.ReqWearingMedal()
    # print(json_response)
    if not json_response['code']:
        data = json_response['data']
        if data:
            # print(data['roominfo']['room_id'], data['today_feed'], data['day_limit'])
            return [(data['roominfo']['room_id'],  int(data['day_limit']) - int(data['today_feed']), data['medal_name']), ]
        else:
            # print('暂无佩戴任何勋章')
            return []

        # web api返回值信息少

async def TitleInfo():
    json_response = await bilibili.ReqTitleInfo()
    dic_title = ConfigLoader().dic_title
    # print(json_response)
    if not json_response['code']:
        data = json_response['data']
        for i in data['list']:
            if i['level']:
                max = i['level'][1]
            else:
                max = '-'
            print(dic_title[i['title_pic']['id']], i['activity'], i['score'], max)

async def fetch_medal(show=True, list_wanted_medal=None):
    printlist = []
    list_medal = []
    if show:
        printlist.append('查询勋章信息')
        printlist.append(
            '{} {} {:^12} {:^10} {} {:^6} {}'.format(adjust_for_chinese('勋章'), adjust_for_chinese('主播昵称'), '亲密度', '今日的亲密度', adjust_for_chinese('排名'), '勋章状态', '房间号码'))
    dic_worn = {'1': '正在佩戴', '0': '待机状态'}
    json_response = await bilibili.request_fetchmedal()
    # print(json_response)
    if not json_response['code']:
        for i in json_response['data']['fansMedalList']:
            if 'roomid' in i:
                list_medal.append((i['roomid'], int(i['dayLimit']) - int(i['todayFeed']), i['medal_name'], i['level']))
                if show:
                    printlist.append('{} {} {:^14} {:^14} {} {:^6} {:^9}'.format(adjust_for_chinese(i['medal_name'] + '|' + str(i['level'])), adjust_for_chinese(i['anchorInfo']['uname']), str(i['intimacy']) + '/' + str(i['next_intimacy']), str(i['todayFeed']) + '/' + str(i['dayLimit']), adjust_for_chinese(str(i['rank'])), dic_worn[str(i['status'])], i['roomid']))
        if show:
            printer.info(printlist, True)
        if list_wanted_medal is not None:
            list_return_medal = []
            for roomid in list_wanted_medal:
                for i in list_medal:
                    if i[0] == roomid:
                        list_return_medal.append(i[:3])
                        break
        else:
            list_return_medal = [i[:3] for i in sorted(list_medal, key=itemgetter(3), reverse=True)]
        return list_return_medal

async def send_danmu_msg_web(msg, roomId):
    json_response = await bilibili.request_send_danmu_msg_web(msg, roomId)
    print(json_response)

async def find_live_user_roomid(wanted_name):
    print(wanted_name)
    
    def check_name_piece(json_rsp, wanted_name):
        results = json_rsp['result']
        if results is None:
            # print('屏蔽全名')
            return None
        for i in results:
            real_name = re.sub(r'<[^>]*>', '', i['uname'])
            # print('去除干扰', real_name)
            if real_name == wanted_name:
                print('找到结果', i)
                return i
        return None
                
    for i in range(len(wanted_name), 0, -1):
        name_piece = wanted_name[:i]
        json_rsp = await bilibili.request_search_biliuser(name_piece)
        answer = check_name_piece(json_rsp, wanted_name)
        if answer is not None:
            return answer['room_id']
        # print('结束一次')

    print('第2备份启用')
    for i in range(len(wanted_name)):
        name_piece = wanted_name[i:]
        json_rsp = await bilibili.request_search_biliuser(name_piece)
        answer = check_name_piece(json_rsp, wanted_name)
        if answer is not None:
            return answer['room_id']

    print('第3备份启用')
    for i in range(len(wanted_name), 0, -1):
        name_piece = wanted_name[:i]
        json_rsp = await bilibili.request_search_liveuser(name_piece)
        answer = check_name_piece(json_rsp, wanted_name)
        if answer is not None:
            return answer['roomid']

    print('第4备份启用')
    for i in range(len(wanted_name)):
        name_piece = wanted_name[i:]
        json_rsp = await bilibili.request_search_liveuser(name_piece)
        answer = check_name_piece(json_rsp, wanted_name)
        if answer is not None:
            return answer['roomid']


async def fetch_capsule_info():
    json_response = await bilibili.request_fetch_capsule()
    # print(json_response)
    if not json_response['code']:
        data = json_response['data']
        if data['colorful']['status']:
            print(f'梦幻扭蛋币: {data["colorful"]["coin"]}个')
        else:
            print('梦幻扭蛋币暂不可用')

        data = json_response['data']
        if data['normal']['status']:
            print(f'普通扭蛋币: {data["normal"]["coin"]}个')
        else:
            print('普通扭蛋币暂不可用')

async def open_capsule(count):
    json_response = await bilibili.request_open_capsule(count)
    # print(json_response)
    if not json_response['code']:
        # print(json_response['data']['text'])
        for i in json_response['data']['text']:
            print(i)

async def watch_living_video(cid):
    import sound
    sound.set_honors_silent_switch(False)
    sound.set_volume(1)
    sound.play_effect('piano:D3')
    json_response = await bilibili.request_playurl(cid)
    print(json_response)
    if not json_response['code']:
        data = json_response['data']
        print(data)
        webbrowser.open(data)

async def fetch_user_info():
    json_response = await bilibili.request_fetch_user_info()
    json_response_ios = await bilibili.request_fetch_user_infor_ios()
    print('[{}] 查询用户信息'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    if not json_response_ios['code']:
        gold_ios = json_response_ios['data']['gold']
    # print(json_response_ios)
    if not json_response['code']:
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
        response_face = await bilibili.request_load_img(userInfo['face'])
        img = Image.open(BytesIO(await response_face.read()))
        img.thumbnail(size)
        try:
            img.show()
        except:
            pass
        print(f'# 手机认证状况 {mobile_verify} | 实名认证状况 {identification}')
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

async def fetch_bag_list(verbose=False, bagid=None, show=True):
    json_response = await bilibili.request_fetch_bag_list()
    gift_list = []
    # print(json_response)
    if show:
        print('[{}] 查询可用礼物'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    for i in json_response['data']['list']:
        bag_id = i['bag_id']
        gift_id = i['gift_id']
        gift_num = i['gift_num']
        gift_name = i['gift_name']
        expireat = i['expire_at']
        left_time = (expireat - json_response['data']['time'])
        if not expireat:
            left_days = '+∞'.center(6)
            left_time = None
        else:
            left_days = round(left_time / 86400, 1)
        if bagid is not None:
            if bag_id == int(bagid):
                return gift_id, gift_num
        else:
            if verbose:
                print(f'# 编号为{bag_id}的{gift_name:^3}X{gift_num:^4} (在{left_days:^6}天后过期)')
            elif show:
                print(f'# {gift_name:^3}X{gift_num:^4} (在{left_days:^6}天后过期)')

        gift_list.append([gift_id, gift_num, bag_id, left_time])
    # print(gift_list)
    return gift_list

async def check_taskinfo():
    json_response = await bilibili.request_check_taskinfo()
    # print(json_response)
    if not json_response['code']:
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
            print(f'## 一共{box_info["max_times"]}次重置次数，当前为第{box_info["freeSilverTimes"]}次第{box_info["type"]}个礼包(每次3个礼包)')

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
    json_response = await bilibili.request_check_room(roomid)
    if not json_response['code']:
        # print(json_response)
        print('查询结果:')
        data = json_response['data']

        if not data['short_id']:
            print('# 此房间无短房号')
        else:
            print(f'# 短号为:{data["short_id"]}')
        print(f'# 真实房间号为:{data["room_id"]}')
        return data['room_id']
    # 房间不存在
    elif json_response['code'] == 60004:
        print(json_response['msg'])

async def send_gift_web(roomid, num_wanted, bagid, giftid=None):
    if giftid is None:
        giftid, num_owned = await fetch_bag_list(False, bagid)
        num_wanted = min(num_owned, num_wanted)
    json_response = await bilibili.request_check_room(roomid)
    ruid = json_response['data']['uid']
    biz_id = json_response['data']['room_id']
    # 200027 不足数目
    json_response1 = await bilibili.request_send_gift_web(giftid, num_wanted, bagid, ruid, biz_id)
    if not json_response1['code']:
        # print(json_response1['data'])
        print(f'# 送出礼物: {json_response1["data"]["gift_name"]}X{json_response1["data"]["gift_num"]}')
    else:
        print("# 错误", json_response1['msg'], roomid, num_wanted, bagid, giftid)

async def fetch_liveuser_info(real_roomid):
    json_response = await bilibili.request_fetch_liveuser_info(real_roomid)
    if not json_response['code']:
        data = json_response['data']
        # print(data)
        print(f'# 主播姓名 {data["info"]["uname"]}')

        uid = data['level']['uid']  # str
        json_response_fan = await bilibili.request_fetch_fan(real_roomid, uid)
        # print(json_response_fan)
        data_fan = json_response_fan['data']
        if not json_response_fan['code'] and data_fan['medal']['status'] == 2:
            print(f'# 勋章名字: {data_fan["list"][0]["medal_name"]}')
        else:
            print('# 该主播暂时没有开通勋章')  # print(json_response_fan)

        size = 100, 100
        response_face = await bilibili.request_load_img(data['info']['face'])
        img = Image.open(BytesIO(await response_face.read()))
        img.thumbnail(size)
        try:
            img.show()
        except:
            pass

async def enter_room(roomid):
    json_response = await bilibili.request_check_room(roomid)

    if not json_response['code']:
        data = json_response['data']
        param1 = data['is_hidden']
        param2 = data['is_locked']
        param3 = data['encrypted']
        if any((param1, param2, param3)):
            printer.info([f'抽奖脚本检测到房间{roomid:^9}为异常房间'], True)
            printer.warn(f'抽奖脚本检测到房间{roomid:^9}为异常房间')
            return False
        else:
            await bilibili.post_watching_history(roomid)
            return True

async def GiveCoin2Av(video_id, num):
    if num not in (1, 2):
        return False
    # 10004 稿件已经被删除
    # 34005 超过，满了
    # -104 不足硬币
    json_rsp = await bilibili().ReqGiveCoin2Av(video_id, num)
    code = json_rsp['code']
    if not code:
        print(f'给视频av{video_id}投{num}枚硬币成功')
        return True
    else:
        print('投币失败', json_rsp['message'])
        if code == -104:
            return None
        return False

async def GetTopVideoList():
    text_rsp = await bilibili().req_fetch_av()
    list_av = re.findall(r'(?<=www.bilibili.com/video/av)\d+(?=/)', text_rsp)
    list_av = list(set(list_av))
    return list_av

async def fetch_uper_video(list_mid):
    list_av = []
    for mid in list_mid:
        json_rsp = await bilibili().req_fetch_uper_video(mid, 1)
        # print(json_rsp)
        data = json_rsp['data']
        pages = data['pages']
        if data['vlist']:
            list_av += [av['aid'] for av in data['vlist']]
        for page in range(2, pages + 1):
            json_rsp = await bilibili().req_fetch_uper_video(mid, page)
            # print(json_rsp)
            data = json_rsp['data']
            list_av += [av['aid'] for av in data['vlist']]
    # print(len(list_av), list_av)
    return list_av

async def GetVideoCid(video_aid):
    json_rsp = await bilibili().ReqVideoCid(video_aid)
    # print(json_rsp[0]['cid'])
    return (json_rsp[0]['cid'])

async def GetRewardInfo(show=True):
    json_rsp = await bilibili().ReqMasterInfo()
    login = json_rsp['login']
    watch_av = json_rsp['watch_av']
    coins_av = json_rsp['coins_av']
    share_av = json_rsp['share_av']
    level_info = json_rsp["level_info"]
    current_exp = level_info['current_exp']
    next_exp = level_info['next_exp']
    if next_exp == -1:
        next_exp = current_exp
    print(f'# 主站等级值 {level_info["current_level"]}')
    print(f'# 主站经验值 {level_info["current_exp"]}')
    print(f'# 主站剩余值 {- current_exp + next_exp}')
    arrow = int(current_exp * 30 / next_exp)
    line = 30 - arrow
    percent = current_exp / next_exp * 100.0
    process_bar = '# [' + '>' * arrow + '-' * line + ']' + '%.2f' % percent + '%'
    print(process_bar)
    if show:
        print(f'每日登陆：{login} 每日观看：{watch_av} 每日投币经验：{coins_av}/50 每日分享：{share_av}')
    return login, watch_av, coins_av, share_av
    
        
async def FetchRoomArea(roomid):
    json_response = await bilibili.ReqRoomInfo(roomid)

    if not json_response['code']:
        # print(json_response)
        # print(json_response['data']['parent_area_id'])
        return json_response['data']['parent_area_id']
    
