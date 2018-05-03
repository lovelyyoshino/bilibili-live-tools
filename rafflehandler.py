import asyncio


class Rafflehandler:
    __slots__ = ('queue_raffle',)
    instance = None

    def __new__(cls, *args, **kw):
        if not cls.instance:
            cls.instance = super(Rafflehandler, cls).__new__(cls, *args, **kw)
            cls.instance.queue_raffle = asyncio.Queue()
        return cls.instance
        
    async def run(self):
        while True:
            raffle = await self.queue_raffle.get()
            await asyncio.sleep(3)
            list_raffle0 = [self.queue_raffle.get_nowait() for i in range(self.queue_raffle.qsize())]
            list_raffle0.append(raffle)
            list_raffle = list(set(list_raffle0))
                
            # print('过滤完毕')
            # if len(list_raffle) != len(list_raffle0):
                # print('过滤机制起作用')
            
            tasklist = []
            for i in list_raffle:
                task = asyncio.ensure_future(i[0](*i[1]))
                tasklist.append(task)
            
            await asyncio.wait(tasklist, return_when=asyncio.ALL_COMPLETED)
            
                
    @staticmethod
    def Put2Queue(func, value):
        # print('welcome to appending')
        Rafflehandler.instance.queue_raffle.put_nowait((func, value))
        # print('appended')
        return
            
    @staticmethod
    def getlist():
        print('目前TV任务队列状况', Rafflehandler.instance.queue_raffle.qsize())
         

