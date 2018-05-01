import asyncio
import datetime
import time
import Tasks


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return currenttime

class BiliTimer:
    __slots__ = ('jobs',)
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(BiliTimer, cls).__new__(cls, *args, **kw)
            cls.instance.jobs = asyncio.PriorityQueue()
        return cls.instance
        
    async def run(self):
        await Tasks.init()
        while True:
            i = await self.jobs.get()
            currenttime = CurrentTime()
            if i[0] < currenttime + 5:
                await i[2]()
            else:
                sleeptime = i[0] - currenttime
                # print('智能睡眠', sleeptime)
                await asyncio.sleep(max(sleeptime, 0))
                await i[2]()
      
    @staticmethod          
    async def append2list_jobs(func, delay):
        await BiliTimer.instance.jobs.put((CurrentTime() + delay, func.__name__, func))
        # print('添加任务')
        return
        
    @staticmethod
    def getresult():
        print('数目', BiliTimer.instance.jobs.qsize())
        
    
