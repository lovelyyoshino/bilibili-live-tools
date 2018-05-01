import datetime
from bilibili import bilibili


# 13:30  --->  13.5
def decimal_time():
    now = datetime.datetime.now()
    return now.hour + now.minute / 60.0


class Statistics:
    __slots__ = ('activity_id_list', 'TV_id_list', 'pushed_event', 'pushed_TV', 'pushed_captain', 'joined_event', 'joined_TV', 'joined_captain', 'result')
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Statistics, cls).__new__(cls, *args, **kw)
            cls.instance.activity_id_list = []
            # cls.instance.activity_time_list = []
            cls.instance.TV_id_list = []
            # cls.instance.TV_time_list = []
            cls.instance.pushed_event = []
            cls.instance.pushed_TV = []
            cls.instance.pushed_captain = []
            
            cls.instance.joined_event = []
            cls.instance.joined_TV = []
            cls.instance.joined_captain = []
            cls.instance.result = {}
            # cls.instance.TVsleeptime = 185
            # cls.instance.activitysleeptime = 125
        return cls.instance

    @staticmethod
    def add_to_result(type, num):
        inst = Statistics.instance
        inst.result[type] = inst.result.get(type, 0) + int(num)

    @staticmethod
    def getlist():
        inst = Statistics.instance
        # print(inst.joined_event)
        # print(inst.joined_TV)
        print('本次推送活动抽奖次数:', len(inst.pushed_event))
        print('本次推送电视抽奖次数:', len(inst.pushed_TV))
        print('本次推送总督抽奖次数:', len(inst.pushed_captain))
        print()
        print('本次参与活动抽奖次数:', len(inst.joined_event))
        print('本次参与电视抽奖次数:', len(inst.joined_TV))
        print('本次参与总督抽奖次数:', len(inst.joined_captain))

    @staticmethod
    def getresult():
        inst = Statistics.instance
        print('本次参与抽奖结果为：')
        for k, v in inst.result.items():
            print(f'{k}X{v}')

    def delete_0st_activitylist(self):
        del self.activity_id_list[0]
        # del self.activity_time_list[0]

    def delete_0st_TVlist(self):
        del self.TV_id_list[0]
        # del inst.TV_time_list[0]

    @staticmethod
    async def clean_activity():
        inst = Statistics.instance
        # print(inst.id_list)
        if inst.activity_id_list:
            for i in range(0, len(inst.activity_id_list)):
                json_response = await bilibili.get_activity_result(*inst.activity_id_list[0])
                # print(json_response)
                try:
                    if not json_response['code']:
                        data = json_response['data']
                        print(f'# 房间{inst.activity_id_list[0][0]:^9}网页端活动抽奖结果: {data["gift_name"]}X{data["gift_num"]}')
                        inst.add_to_result(data['gift_name'], int(data['gift_num']))
    
                        inst.delete_0st_activitylist()
                    # {'code': -400, 'msg': '尚未开奖，请耐心等待！', 'message': '尚未开奖，请耐心等待！', 'data': []}
                    elif json_response['code'] == -400:
                        # sleepseconds = inst.activitysleeptime + inst.activity_time_list[0] - int(CurrentTime())+ 2
                        # sleepseconds = inst.activity_time_list[0] - int(CurrentTime())
                        # return sleepsecondsq
                        return
    
                    else:
                        print('未知情况')
                        print(json_response)
                except:
                    print(json_response)

        else:
            return

    @staticmethod
    async def clean_TV():
        inst = Statistics.instance
        # print(inst.TV_id_list)
        if inst.TV_id_list:
            for i in range(0, len(inst.TV_id_list)):

                json_response = await  bilibili.get_TV_result(*inst.TV_id_list[0])
                # if response.json()['data']['gift_name'] != "":
                # print(json_response)
                try:
                    # {'code': 0, 'msg': '正在抽奖中..', 'message': '正在抽奖中..', 'data': {'gift_id': '-1', 'gift_name': '', 'gift_num': 0, 'gift_from': '', 'gift_type': 0, 'gift_content': '', 'status': 3}}

                    if json_response['data']['gift_id'] == '-1':
                        return
                    elif json_response['data']['gift_id'] != '-1':
    
                        data = json_response['data']
                        print(f'# 房间{inst.TV_id_list[0][0]:^9}小电视道具抽奖结果: {data["gift_name"]}X{data["gift_num"]}')
                        inst.add_to_result(data['gift_name'], int(data['gift_num']))
    
                        inst.delete_0st_TVlist()
                except:
                    print(json_response)
            # else:
            # print(int(CurrentTime()))
            # sleepseconds = inst.TV_time_list[0] - int(CurrentTime()) + 1
            # sleepseconds = inst.TV_time_list[0] - int(CurrentTime())
            # return

            #  else:
            # print('未知')
        else:
            return

    @staticmethod
    def append_to_activitylist(raffleid, text1, time=''):
        inst = Statistics.instance
        inst.activity_id_list.append((text1, raffleid))
        # inst.activity_time_list.append(int(time))
        # inst.activity_time_list.append(int(CurrentTime()))
        inst.joined_event.append(decimal_time())
        # print("activity加入成功", inst.joined_event)

    @staticmethod
    def append_to_TVlist(raffleid, real_roomid, time=''):
        inst = Statistics.instance
        inst.TV_id_list.append((real_roomid,raffleid))
        # inst.TV_time_list.append(int(time)+int(CurrentTime()))
        # inst.TV_time_list.append(int(CurrentTime()))
        inst.joined_TV.append(decimal_time())
        # print("tv加入成功", inst.joined_TV)
        
    @staticmethod
    def append_to_captainlist():
        inst = Statistics.instance
        inst.joined_captain.append(decimal_time())
        
    @staticmethod
    def append2pushed_activitylist():
        inst = Statistics.instance
        inst.pushed_event.append(decimal_time())
        
    @staticmethod
    def append2pushed_TVlist():
        inst = Statistics.instance
        inst.pushed_TV.append(decimal_time())
        
    @staticmethod
    def append2pushed_captainlist():
        inst = Statistics.instance
        inst.pushed_captain.append(decimal_time())

    @staticmethod
    def check_TVlist(real_roomid, raffleid):
        inst = Statistics.instance
        if (real_roomid, raffleid) not in inst.TV_id_list:
            return True
        return False

    @staticmethod
    def check_activitylist(real_roomid, raffleid):
        inst = Statistics.instance
        if (real_roomid, raffleid) not in inst.activity_id_list:
            return True
        return False
        
    @staticmethod
    def checklist():
        print('目前activity任务队列状况:', Statistics.instance.activity_id_list)
        print('TV:', Statistics.instance.TV_id_list)
