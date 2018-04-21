import sys
from imp import reload
from configloader import ConfigLoader
import hashlib
import random
import datetime
import time
import requests
import base64
import aiohttp
import asyncio

reload(sys)


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return str(currenttime)


def cnn_captcha(img):
    url = "http://101.236.6.31:8080/code"
    data = {"image": img}
    ressponse = requests.post(url, data=data)
    captcha = ressponse.text
    print("此次登录出现验证码,识别结果为%s" % (captcha))
    return captcha


async def replay_request(response):
    json_response = await response.json(content_type=None)
    if json_response['code'] == 1024:
        print('b站炸了，暂停所有请求5s后重试，请耐心等待')
        await asyncio.sleep(5)
        return True
    else:
        return False

base_url = 'https://api.live.bilibili.com'

        
class bilibili():
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(bilibili, cls).__new__(cls, *args, **kw)
            cls.instance.dic_bilibili = ConfigLoader().dic_bilibili
            cls.instance.bili_session = None
        return cls.instance
    
    @property
    def bili_section(self):
        if self.bili_session is None:
            self.bili_session = aiohttp.ClientSession()
            # print(0)
        return self.bili_session
        
    def calc_sign(self, str):
        str = str + self.dic_bilibili['app_secret']
        hash = hashlib.md5()
        hash.update(str.encode('utf-8'))
        sign = hash.hexdigest()
        return sign
        
    def load_session(self, dic):
        # print(dic)
        for i in dic.keys():
            self.dic_bilibili[i] = dic[i]
            if i == 'cookie':
                self.dic_bilibili['pcheaders']['cookie'] = dic[i]
                self.dic_bilibili['appheaders']['cookie'] = dic[i]
    
    async def bili_section_post(self, url, headers=None, data=None):
        while True:
            try:
                response = await self.bili_section.post(url, headers=headers, data=data)
                tag = await replay_request(response)
                if tag:
                    continue
                return response
            except:
                # print('当前网络不好，正在重试，请反馈开发者!!!!')
                # print(sys.exc_info()[0], sys.exc_info()[1])
                continue
        
        
    async def bili_section_get(self, url, headers=None, data=None, params=None):
        while True:
            try:
                response = await self.bili_section.get(url, headers=headers, data=data, params=params)
                tag = await replay_request(response)
                if tag:
                    continue
                return response
            except:
                # print('当前网络不好，正在重试，请反馈开发者!!!!')
                # print(sys.exc_info()[0], sys.exc_info()[1])
                continue
                
    async def request_playurl(self, cid):
        # cid real_roomid
        # url = 'http://api.live.bilibili.com/room/v1/Room/playUrl?'
        url = '{}/api/playurl?device=phone&platform=ios&scale=3&build=10000&cid={}&otype=json&platform=h5'.format(base_url, cid)
        response = await self.bili_section_get(url)
        return response
                
    def request_search_user(self, name):
        search_url = "https://search.bilibili.com/api/search?search_type=bili_user&keyword=" + name
        response = requests.get(search_url)
        return response
    
    async def request_fetch_capsule(self):
        url = "{}/api/ajaxCapsule".format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response
        
    async def request_open_capsule(self, count):
        url = "{}/api/ajaxCapsuleOpen".format(base_url)
        data = {
            'type': 'normal',
            "count": count,
            "csrf_token": self.dic_bilibili['csrf']
        }
        response = await self.bili_section_post(url, data=data, headers=self.dic_bilibili['pcheaders'])
        return response
                
    def request_logout(self):
        url = 'https://passport.bilibili.com/login?act=exit'
        pcheaders = self.dic_bilibili['pcheaders'].copy()
        pcheaders['Host'] = "passport.bilibili.com"
        response = requests.get(url, headers=pcheaders)
        return response
        
    # 1:900兑换
    async def request_doublegain_coin2silver(self):
        # url: "/exchange/coin2silver",
        data = {'coin': 10}
        url = "{}/exchange/coin2silver".format(base_url)
        response = await self.bili_section_post(url, data=data, headers=self.dic_bilibili['pcheaders'])
        return response
        
    async def post_watching_history(self, room_id):
        data = {
            "room_id": room_id,
            "csrf_token": self.dic_bilibili['csrf']
        }
        url = "{}/room/v1/Room/room_entry_action".format(base_url)
        response = await self.bili_section_post(url, data=data, headers=self.dic_bilibili['pcheaders'])
        return response

    async def silver2coin_web(self):
        url = "{}/exchange/silver2coin".format(base_url)
        response = await self.bili_section_post(url, headers=self.dic_bilibili['pcheaders'])
        return response
        
    async def silver2coin_app(self):
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + '&mobi_app=' + self.dic_bilibili[
                          'mobi_app'] + '&platform=' + self.dic_bilibili['platform'] + '&ts=' + CurrentTime()
        sign = self.calc_sign(temp_params)
        app_url = "{}/AppExchange/silver2coin?{}&sign={}".format(base_url, temp_params, sign)
        response1 = await self.bili_section_post(app_url, headers=self.dic_bilibili['appheaders'])
        return response1
        
    async def request_fetch_fan(self, real_roomid, uid):
        url = '{}/rankdb/v1/RoomRank/webMedalRank?roomid={}&ruid={}'.format(base_url, real_roomid, uid)
        response = await self.bili_section_get(url)
        return response
        
    async def request_check_room(self, roomid):
        url = "{}/room/v1/Room/room_init?id={}".format(base_url, roomid)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response

    async def request_fetch_bag_list(self):
        url = "{}/gift/v2/gift/bag_list".format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response
        
    async def request_check_taskinfo(self):
        url = '{}/i/api/taskInfo'.format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response

    async def request_send_gift_web(self, giftid, giftnum, bagid, ruid, biz_id):
        url = "{}/gift/v2/live/bag_send".format(base_url)
        data = {
            'uid': self.dic_bilibili['uid'],
            'gift_id': giftid,
            'ruid': ruid,
            'gift_num': giftnum,
            'bag_id': bagid,
            'platform': 'pc',
            'biz_code': 'live',
            'biz_id': biz_id,
            'rnd': CurrentTime(),
            'storm_beat_id': '0',
            'metadata': '',
            'price': '0',
            'csrf_token': self.dic_bilibili['csrf']
        }
        response = await self.bili_section_post(url, headers=self.dic_bilibili['pcheaders'], data=data)
        return response

    async def request_fetch_user_info(self):
        url = "{}/i/api/liveinfo".format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response
        
    async def request_fetch_user_infor_ios(self):
        # 长串请求起作用的就这几个破玩意儿
        url = '{}/mobile/getUser?access_key={}&platform=ios'.format(base_url, self.dic_bilibili['access_key'])
        response = await self.bili_section_get(url)
        return response
        
    async def request_fetch_liveuser_info(self, real_roomid):
        url = '{}/live_user/v1/UserInfo/get_anchor_in_room?roomid={}'.format(base_url, real_roomid)
        response = await self.bili_section_get(url)
        return response
        
    def request_load_img(self, url):
        return requests.get(url)

    async def request_send_danmu_msg_andriod(self, msg, roomId):
        url = '{}/api/sendmsg?'.format(base_url)
        # page ??
        time = CurrentTime()
        list_url = ["access_key=" + self.dic_bilibili['access_key'], "appkey=" + self.dic_bilibili['appkey'], 'aid=',
                    'page=1', "build=" + self.dic_bilibili['build']]
        sign = self.calc_sign('&'.join(sorted(list_url)))

        url = url + '&'.join(list_url[:3] + ['sign=' + sign] + list_url[3:])

        data = {
            'access_key': self.dic_bilibili['access_key'],
            'actionKey': "appkey",
            'appkey': self.dic_bilibili['appkey'],
            'build': self.dic_bilibili['build'],
            # 房间号
            'cid': roomId,
            # 颜色
            'color': '16777215',
            'device': self.dic_bilibili['device'],
            # 字体大小
            'fontsize': '25',
            # 实际上并不需要包含 mid 就可以正常发送弹幕, 但是真实的 Android 客户端确实发送了 mid
            # 自己的用户 ID!!!!
            'from': '',
            # 'mid': '1008****'
            'mobi_app': self.dic_bilibili['mobi_app'],
            # 弹幕模式
            # 1 普通  4 底端  5 顶端 6 逆向  7 特殊   9 高级
            # 一些模式需要 VIP
            'mode': '1',
            # 内容
            "msg": msg,
            'platform': self.dic_bilibili['platform'],
            # 播放时间
            'playTime': '0.0',
            # 弹幕池  尚且只见过为 0 的情况
            'pool': '0',
            # random   随机数
            # 在 web 端发送弹幕, 该字段是固定的, 为用户进入直播页面的时间的时间戳. 但是在 Android 端, 这是一个随机数
            # 该随机数不包括符号位有 9 位
            # '1367301983632698015'
            'rnd': str((int)(1000000000000000000.0 + 2000000000000000000.0 * random.random())),
            "screen_state": '',
            # 反正不管用 没实现的
            'sign': sign,
            'ts': time,
            # 必须为 "json"
            'type': "json"
        }
        # print('send msg app')

        response = await self.bili_section_post(url, headers=self.dic_bilibili['appheaders'], data=data)
        return response

    async def request_send_danmu_msg_web(self, msg, roomId):
        url = '{}/msg/send'.format(base_url)
        data = {
            'color': '16777215',
            'fontsize': '25',
            'mode': '1',
            'msg': msg,
            'rnd': '0',
            'roomid': roomId,
            'csrf_token': self.dic_bilibili['csrf']
        }

        response = await self.bili_section_post(url, headers=self.dic_bilibili['pcheaders'], data=data)
        return response

    async def request_fetchmedal(self):
        url = '{}/i/api/medal?page=1&pageSize=50'.format(base_url)
        response = await self.bili_section_post(url, headers=self.dic_bilibili['pcheaders'])
        return response
        
    def request_getkey(self):
        url = 'https://passport.bilibili.com/api/oauth2/getKey'
        temp_params = 'appkey=' + self.dic_bilibili['appkey']
        sign = self.calc_sign(temp_params)
        params = {'appkey': self.dic_bilibili['appkey'], 'sign': sign}
        response = requests.post(url, data=params)
        return response
        
    def normal_login(self, username, password):
        # url = 'https://passport.bilibili.com/api/oauth2/login'   //旧接口
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        temp_params = 'appkey=' + self.dic_bilibili['appkey'] + '&password=' + password + '&username=' + username
        sign = self.calc_sign(temp_params)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        payload = "appkey=" + self.dic_bilibili[
            'appkey'] + "&password=" + password + "&username=" + username + "&sign=" + sign
        response = requests.post(url, data=payload, headers=headers)
        return response
        
    def login_with_captcha(self, username, password):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Host': 'passport.bilibili.com',
            'cookie': "sid=hxt5szbb"
        }
        s = requests.session()
        url = "https://passport.bilibili.com/captcha"
        res = s.get(url, headers=headers)
        tmp1 = base64.b64encode(res.content)
        
        captcha = cnn_captcha(tmp1)
        temp_params = 'actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&captcha=' + captcha + '&device=' + self.dic_bilibili['device'] + '&mobi_app=' + self.dic_bilibili['mobi_app'] + '&password=' + password + '&platform=' + self.dic_bilibili[
                          'platform'] + '&username='+username
        sign = self.calc_sign(temp_params)
        payload = temp_params + '&sign=' + sign
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['cookie'] = "sid=hxt5szbb"
        url = "https://passport.bilibili.com/api/v2/oauth2/login"
        response = s.post(url, data=payload, headers=headers)
        return response
        
    def request_check_token(self):
        list_url = ["access_key=" + self.dic_bilibili['access_key'], "appkey=" + self.dic_bilibili['appkey'], "access_token=" + self.dic_bilibili['access_key'], 'actionKey=' + self.dic_bilibili[
            'actionKey'], 'build=' + self.dic_bilibili[
                          'build'], 'device=' + self.dic_bilibili['device'], 'mobi_app=' + self.dic_bilibili[
                          'mobi_app'], 'platform=' + self.dic_bilibili['platform'], 'ts=' + CurrentTime()]
        list_cookie = self.dic_bilibili['cookie'].split(';')[:-1]
        params = ('&'.join(sorted(list_url + list_cookie)))
        sign = self.calc_sign(params)
        appheaders = self.dic_bilibili['appheaders'].copy()
        appheaders['Host'] = "passport.bilibili.com"
        true_url = 'https://passport.bilibili.com/api/v2/oauth2/info?' + params + '&sign=' + sign
        response1 = requests.get(true_url, headers=appheaders)
        return response1
        
    def request_refresh_token(self):
        data = {
            "access_token": self.dic_bilibili['access_key'],
            "appkey": self.dic_bilibili['appkey'],
            "refresh_token": self.dic_bilibili['refresh_token']
            }
        str_data = '&'.join('{}={}'.format(key,val) for (key, val) in data.items())
        data['sign'] = self.calc_sign(str_data)
        url = 'https://passport.bilibili.com/api/oauth2/refreshToken'
        appheaders = self.dic_bilibili['appheaders'].copy()
        appheaders['Host'] = "passport.bilibili.com"
        response1 = requests.post(url, headers=appheaders, params=data)
        return response1
    
    async def get_giftlist_of_storm(self, dic):
        roomid = dic['roomid']
        get_url = "{}/lottery/v1/Storm/check?roomid={}".format(base_url, roomid)
        response = await self.bili_section_get(get_url, headers=self.dic_bilibili['pcheaders'])
        return response
        
    async def get_gift_of_storm(self, id):
        storm_url = '{}/lottery/v1/Storm/join'.format(base_url)
        payload = {
            "id": id,
            "color": "16777215",
            "captcha_token": "",
            "captcha_phrase": "",
            "token": "",
            "csrf_token": self.dic_bilibili['csrf']}
        response1 = await self.bili_section_post(storm_url, data=payload, headers=self.dic_bilibili['pcheaders'])
        return response1
        
    async def get_gift_of_events_web(self, text1, text2, raffleid):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'cookie': self.dic_bilibili['cookie'],
            'referer': text2
        }
        pc_url = '{}/activity/v1/Raffle/join?roomid={}&raffleId={}'.format(base_url, text1, raffleid)
        pc_response = await self.bili_section_get(pc_url, headers=headers)

        return pc_response

    async def get_gift_of_events_app(self, text1, text2, raffleid):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'cookie': self.dic_bilibili['cookie'],
            'referer': text2
        }
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + '&event_type=flower_rain-' + str(
            raffleid) + '&mobi_app=' + self.dic_bilibili['mobi_app'] + '&platform=' + self.dic_bilibili[
                          'platform'] + '&room_id=' + str(
            text1) + '&ts=' + CurrentTime()
        params = temp_params + self.dic_bilibili['app_secret']
        sign = self.calc_sign(temp_params)
        true_url = '{}/YunYing/roomEvent?{}&sign={}'.format(base_url, temp_params, sign)
        response1 = await self.bili_section_get(true_url, params=params, headers=headers)
        return response1

    async def get_gift_of_TV(self, real_roomid, raffleid):
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + '&id=' + str(
            raffleid) + '&mobi_app=' + self.dic_bilibili['mobi_app'] + '&platform=' + self.dic_bilibili[
                          'platform'] + '&roomid=' + str(
            real_roomid) + '&ts=' + CurrentTime()
        sign = self.calc_sign(temp_params)
        true_url = '{}/AppSmallTV/join?{}&sign={}'.format(base_url, temp_params, sign)
        response2 = await self.bili_section_get(true_url, headers=self.dic_bilibili['appheaders'])
        return response2

    async def get_gift_of_captain(self, roomid, id):
        join_url = "{}/lottery/v1/lottery/join".format(base_url)
        payload = {"roomid": roomid, "id": id, "type": "guard", "csrf_token": self.dic_bilibili['csrf']}
        response2 = await self.bili_section_post(join_url, data=payload, headers=self.dic_bilibili['pcheaders'])
        return response2

    async def get_giftlist_of_events(self, text1):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'accept-encoding': 'gzip, async deflate',
            'Host': 'api.live.bilibili.com',
        }
        url = '{}/activity/v1/Raffle/check?roomid={}'.format(base_url, text1)
        response = await self.bili_section_get(url, headers=headers)

        return response

    async def get_giftlist_of_TV(self, real_roomid):
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + \
                      '&mobi_app=' + self.dic_bilibili['mobi_app'] + '&platform=' + self.dic_bilibili[
                          'platform'] + '&roomid=' + str(
            real_roomid) + '&ts=' + CurrentTime()
        sign = self.calc_sign(temp_params)
        check_url = '{}/AppSmallTV/index?{}&sign={}'.format(base_url,temp_params, sign)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        }
        response = await self.bili_section_get(check_url, headers=headers)

        return response

    async def get_giftlist_of_captain(self, roomid):
        true_url = '{}/lottery/v1/lottery/check?roomid={}'.format(base_url, roomid)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q = 0.8",
            "Accept-Encoding": "gzip,async deflate,br",
            "Accept-Language": "zh-CN",
            "DNT": "1",
            "Cookie": "LIVE_BUVID=AUTO7715232653604550",
            "Connection": "keep-alive",
            "Cache-Control": "max-age =0",
            "Host": "api.live.bilibili.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0'
        }
        response1 = await self.bili_section_get(true_url, headers=headers)
        return response1

    def get_giftids_raffle(self, str):
        return self.dic_bilibili['giftids_raffle'][str]

    def get_giftids_raffle_keys(self):
        return self.dic_bilibili['giftids_raffle'].keys()

    async def get_activity_result(self, activity_roomid, activity_raffleid):
        url = "{}/activity/v1/Raffle/notice?roomid={}&raffleId={}".format(base_url, activity_roomid, activity_raffleid)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'accept-encoding': 'gzip, async deflate',
            'Host': 'api.live.bilibili.com',
            'cookie': self.dic_bilibili['cookie'],
        }
        response = await self.bili_section_get(url, headers=headers)
        return response

    async def get_TV_result(self, TV_roomid, TV_raffleid):
        url = "{}/gift/v2/smalltv/notice?roomid={}&raffleId={}".format(base_url, TV_roomid, TV_raffleid)
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'accept-encoding': 'gzip, async deflate',
            'Host': 'api.live.bilibili.com',
            'cookie': self.dic_bilibili['cookie'],
        }
        response = await self.bili_section_get(url, headers=headers)
        return response

    async def pcpost_heartbeat(self):
        url = '{}/User/userOnlineHeart'.format(base_url)
        response = await self.bili_section_post(url, headers=self.dic_bilibili['pcheaders'])
        return response

    # 发送app心跳包
    async def apppost_heartbeat(self):
        time = CurrentTime()
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + '&mobi_app=' + self.dic_bilibili[
                          'mobi_app'] + '&platform=' + self.dic_bilibili['platform'] + '&ts=' + time
        sign = self.calc_sign(temp_params)
        url = '{}/mobile/userOnlineHeart?{}&sign={}'.format(base_url, temp_params, sign)
        payload = {'roomid': 23058, 'scale': 'xhdpi'}
        response = await self.bili_section_post(url, data=payload, headers=self.dic_bilibili['appheaders'])
        return response

    # 心跳礼物
    async def heart_gift(self):
        url = "{}/gift/v2/live/heart_gift_receive?roomid=3&area_v2_id=34".format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response

    async def get_lotterylist(self, i):
        url = "{}/lottery/v1/box/getStatus?aid={}".format(base_url, i)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response

    async def get_gift_of_lottery(self, i, g):
        url1 = '{}/lottery/v1/box/draw?aid={}&number={}'.format(base_url, i, g + 1)
        response1 = await self.bili_section_get(url1, headers=self.dic_bilibili['pcheaders'])
        return response1

    async def get_time_about_silver(self):
        time = CurrentTime()
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + '&mobi_app=' + self.dic_bilibili[
                          'mobi_app'] + '&platform=' + self.dic_bilibili['platform'] + '&ts=' + time
        sign = self.calc_sign(temp_params)
        GetTask_url = '{}/mobile/freeSilverCurrentTask?{}&sign={}'.format(base_url, temp_params, sign)
        response = await self.bili_section_get(GetTask_url, headers=self.dic_bilibili['appheaders'])
        return response

    async def get_silver(self, timestart, timeend):
        time = CurrentTime()
        temp_params = 'access_key=' + self.dic_bilibili['access_key'] + '&actionKey=' + self.dic_bilibili[
            'actionKey'] + '&appkey=' + self.dic_bilibili['appkey'] + '&build=' + self.dic_bilibili[
                          'build'] + '&device=' + self.dic_bilibili['device'] + '&mobi_app=' + self.dic_bilibili[
                          'mobi_app'] + '&platform=' + self.dic_bilibili[
                          'platform'] + '&time_end=' + timeend + '&time_start=' + timestart + '&ts=' + time
        sign = self.calc_sign(temp_params)
        url = '{}/mobile/freeSilverAward?{}&sign={}'.format(base_url, temp_params, sign)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['appheaders'])
        return response

    async def get_dailybag(self):
        url = '{}/gift/v2/live/receive_daily_bag'.format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response

    async def get_dosign(self):
        url = '{}/sign/doSign'.format(base_url)
        response = await self.bili_section_get(url, headers=self.dic_bilibili['pcheaders'])
        return response

    async def get_dailytask(self):
        url = '{}/activity/v1/task/receive_award'.format(base_url)
        payload2 = {'task_id': 'double_watch_task'}
        response2 = await self.bili_section_post(url, data=payload2, headers=self.dic_bilibili['appheaders'])
        return response2

    def get_grouplist(self):
        url = "https://api.vc.bilibili.com/link_group/v1/member/my_groups"
        pcheaders = self.dic_bilibili['pcheaders'].copy()
        pcheaders['Host'] = "api.vc.bilibili.com"
        response = requests.get(url, headers=pcheaders)
        return response

    def assign_group(self, i1, i2):
        temp_params = "_device=" + self.dic_bilibili[
            'device'] + "&_hwid=SX1NL0wuHCsaKRt4BHhIfRguTXxOfj5WN1BkBTdLfhstTn9NfUouFiUV&access_key=" + \
                      self.dic_bilibili['access_key'] + "&appkey=" + self.dic_bilibili['appkey'] + "&build=" + \
                      self.dic_bilibili['build'] + "&group_id=" + str(i1) + "&mobi_app=" + self.dic_bilibili[
                          'mobi_app'] + "&owner_id=" + str(i2) + "&platform=" + self.dic_bilibili[
                          'platform'] + "&src=xiaomi&trace_id=20171224024300024&ts=" + CurrentTime() + "&version=5.20.1.520001"
        sign = self.calc_sign(temp_params)
        url = "https://api.vc.bilibili.com/link_setting/v1/link_setting/sign_in?" + temp_params + "&sign=" + sign
        appheaders = self.dic_bilibili['appheaders'].copy()
        appheaders['Host'] = "api.vc.bilibili.com"
        response = requests.get(url, headers=appheaders)
        return response

    async def gift_list(self):
        url = "{}/gift/v2/live/room_gift_list?roomid=2721650&area_v2_id=86".format(base_url)
        res = await self.bili_section_get(url)
        return res
        
