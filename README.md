
# bilibili-live-tools
单用户比利脚本

yjqiang分支是一个次分支，特别感谢主分支所有参与者的基础奠定

docker使用 https://github.com/Muromi-Rikka/bilibili-live-tools-docker  
docker使用  https://github.com/zsnmwy/bilibili-live-tools-docker

pythonista3(ios) https://www.jianshu.com/p/669e63b5ec2b

依赖包 https://github.com/yjqiang/bilibili-live-tools/blob/master/requirements.txt  
运行方法  run.py

多用户版本 https://github.com/yjqiang/bili2.0  
二次开发 https://github.com/Hsury/Bilibili-Toolkit  

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
        根据亲密度赠送礼物
        银瓜子硬币双向兑换
        云端验证码识别
        主站每日任务（4个）

version 1.0.0
------
      基本稳定

version 1.1.0
------
      抽奖繁忙重试机制建立（目前只支持了tv，因为只有这一个code）
      开始使用f string代替字符串加法或者format，f string大法好
      修复b站sb的屏蔽”御姐”用户名关键词这种（倒着切查，其实应该分词查看）
      结构方面的调整，一些不必要的对象创建被删除
      简单调整代码style
      其他细节的改变

version 2.0
------
      摩天大楼多房间
      主站功能（投币分享等）支持
      websocket弹幕
      总督领取
      token refresh and save cookie 
      Queue队列
      其他细节的改变   

version 2.1
------
      更新api
      v4小电视更新
      支持风纪委员会
      其他修改  

version 2.2
------
      更新wiki  
      调整bilitimer,改善漏抽问题  
      弹幕重连机制修复  
      实物抽奖机制优化  

version 3.0  
------
      庆祝多用户发布  
      风纪委基本100%成功率
    
      

        


环境:
------  
        python3.6+
  
    


感谢:https://github.com/lyyyuna

感谢:https://github.com/lkeme/BiliHelper

感谢:https://github.com/czp3009/bilibili-api  

感谢:https://github.com/lzghzr/bilive_client


本项目采用MIT开源协议
