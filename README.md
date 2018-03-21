# bilibili-live-tools

 Dawnnnnnn作者重构后就拿来用了，立个FLAG，等我今年忙完好好研究bilibili，风暴等也有一些想法，可惜最近没时间去完成了

目前已完成：

        每日签到
        双端心跳领取经验
        领取银瓜子宝箱
        提交每日任务
        漫天花雨双端抽奖
        小电视PC端抽奖
        领取每日包裹奖励
        应援团签到
        实物抽奖(实验性)
        获取心跳礼物(实验性)
        节奏风暴领取(单文件实验性)


环境:
    
        python3.5+

第三方库配置:

        pip install requests
        pip install rsa
        pip install aiohttp

更新说明(3.21):

        实物抽奖为实验性功能，只过滤了“测试”关键字，功能默认开启，风险在pull requests中有说明,
        如不想打开本功能，请用记事本编辑OnlineHeart.py文件的最后几行，将“self.draw_lottery()“这行删掉即可

使用方法：

        python run.py
    
        然后输入好几遍账号密码就行了233333

引用代码作者github:https://github.com/lyyyuna

本项目采用MIT开源协议




