
# bilibili-live-tools


项目又经过了一天的重构。差不多能当python课设交上去了(´；ω；`)

学业繁忙，准备弃坑咕咕咕(flag)，风暴初版已上传，不再更新后几版

//时隔多日打算学一下图形化，说不定会以这个项目作为样本(flag)


目前已完成：
------

        每日签到
        双端心跳领取经验
        领取银瓜子宝箱
        提交每日任务
        漫天花雨双端抽奖
        小电视PC端抽奖
        领取每日包裹奖励
        应援团签到
        获取心跳礼物
        20倍节奏风暴领取
        获取总督开通奖励
        实物抽奖
        清空当日到期礼物
        银瓜子兑换硬币

        
更新说明
------

3.21:
        
    实物抽奖为实验性功能，只过滤了“测试”关键字，功能默认开启，风险在pull requests中有说明,
    如不想打开本功能，请用记事本编辑OnlineHeart.py文件的最后几行，将“self.draw_lottery()“这行删掉即可

3.22:
        
>   在[Shadow-D](https://github.com/Shadow-D)大佬的指导下，重新写了父类，实现了输入一次账密通用cookie的功能，
    同时加上了获取pc端抽奖结果的功能
    
3.23:

    紧急修复部分账号PC端参与小电视抽奖异常的bug
    修复邮箱登录异常的bug
    过滤重复抽奖，一定程度上避免ban ip
3.24:
>  今天[yjqiang](https://github.com/yjqiang)大佬更新了一大堆的东西,格式更加美观了,还发现了一个bug(有空就修了(flag))(见鬼,大佬们都不睡觉的吗.jpg)
   
>  特别提醒：
        最近b站在检测脚本挂机,请慎重考虑是否继续使用该软件,因使用脚本造成封号黑号的请自行承担后果。


3.25:

    美化输出，设定延迟，加入查询功能，采用一定措施防止被封。
    
3.2x:

    记不住了修的bug太多了。
    然后插播一条重要消息，因为代码进行了比较大的变动，导致打包成exe后无法连接到弹幕服务器(玄学)，所以暂时停止release的发布，请尝试搭建python环境
    
3.28:
    
    加入20倍节奏风暴自动领取功能

3.29:
>  感谢[yjqiang](https://github.com/yjqiang)大佬再次重构
   恢复exe版本的提供

>  实现从user.conf中读取账号密码,并默认记住账号密码

>  增加获取总督开通奖励功能

>  重构printer 修复重连时的报错

3.30:
   
    增加一个防钓鱼措施
4.1:

    活动名称显示，总督奖励领取修复，修改结构
4.2:

    添加自动清空快到期礼物的功能，添加银瓜子兑换硬币功能
    on/off 的配置选项：1代表on,0代表off
4.3:

    摸鱼
4.4:

    调整架构，加入获取验证码的功能
环境:
------  
        python3.6

第三方库配置:
------

        pip install -r requirements.txt

使用方法：
------

       第一种:
             自行按照百度配置python运行环境（要把那个PATH的勾上!）,并安装所需第三方库,最后执行python run.py
       第二种:
             下载release中的exe版本,双击运行(已恢复)
       第三种:
             推荐使用ios pythonsta 工具（http://omz-software.com/pythonista/）
             （yjqiang没收广告费）
             备注：由于yjqiang开发者使用ios pythonista，所以优先适配ios，但是其他平台的适配也会加入      
         
        
    
修bug群:473195880


感谢:https://github.com/lyyyuna

感谢:https://github.com/lkeme/BiliHelper

感谢:https://github.com/czp3009/bilibili-api


本项目采用MIT开源协议

