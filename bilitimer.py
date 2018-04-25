import asyncio
import datetime
import time


def CurrentTime():
    currenttime = int(time.mktime(datetime.datetime.now().timetuple()))
    return str(currenttime)

class BiliTimer:
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(BiliTimer, cls).__new__(cls, *args, **kw)
            cls.instance.jobs = []
        return cls.instance
        
    async def run(self):
        while True:
            len_list_jobs = len(self.jobs)
            # print('准备执行')

            
            tasklist = []
            removed_tag = []
            for i in range(len_list_jobs):
                if self.jobs[i][2] + self.jobs[i][3] < int(CurrentTime()) + 10:
                    task = asyncio.ensure_future(self.jobs[i][0](*self.jobs[i][1]))
                    tasklist.append(task)
                    removed_tag.append(i)
            
            if tasklist:
                await asyncio.wait(tasklist, return_when=asyncio.ALL_COMPLETED)
                self.jobs = [i for j, i in enumerate(self.jobs) if j not in removed_tag]
                # print('删除完成工作之后', self.jobs)
                    
                # print('本批次结束')
            recent_time = None
            for i in self.jobs:
                wanted_time = i[2] + i[3]
                # print(wanted_time)
                if recent_time is None or wanted_time < recent_time:
                    recent_time = wanted_time
            sleeptime = - int(CurrentTime()) + recent_time
            # print('智能睡眠', sleeptime)
            await asyncio.sleep(max(sleeptime, 0))
                
    def append2list_jobs(self, job):
        # [func, x(list), starttime(s), delay(s)]
        # print('welcome to appending')
        self.jobs.append(job)
        # print('添加任务', job)
        return
        
    def getresult(self):
        print('目前timer任务队列状况', self.jobs)
        print('数目', len(self.jobs))
        
    
