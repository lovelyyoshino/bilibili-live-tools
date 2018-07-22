import asyncio
import datetime
import time
import Tasks
import printer


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
            sleeptime = i[0] - currenttime
            print('智能睡眠', sleeptime)
            await asyncio.sleep(max(sleeptime, 0))
            try:
                bytes_data = await asyncio.wait_for(i[2](), timeout=15.0)
            except asyncio.TimeoutError:
                printer.warn(i[1])
                printer.warn('timeout')
            except:
                # websockets.exceptions.ConnectionClosed'>
                print(sys.exc_info()[0], sys.exc_info()[1])
                printer.warn(i[1])
                printer.warn('!!!!')
      
    @staticmethod
    async def append2list_jobs(func, delay):
        await BiliTimer.instance.jobs.put((CurrentTime() + delay, func.__name__, func))
        # print('添加任务')
        return
        
    @staticmethod
    def getresult():
        print('数目', BiliTimer.instance.jobs.qsize())
        
    
