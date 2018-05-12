
# bilibili-live-tools


yjqiang分支是一个次分支，特别感谢主分支所有参与者的基础奠定

docker使用 https://github.com/Muromi-Rikka/bilibili-live-tools-docker


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
    基本稳定

version 1.1.0
      抽奖繁忙重试机制建立（目前只支持了tv，因为只有这一个code）
      开始使用f string代替字符串加法或者format，f string大法好
      修复b站sb的屏蔽”御姐”用户名关键词这种（倒着切查，其实应该分词查看）
      结构方面的调整，一些不必要的对象创建被删除
      简单调整代码style
      其他细节的改变

version 2.0
      改了一堆。。。忘了，反正一堆
         
      
        


环境:
------  
        python3.6
  
    


感谢:https://github.com/lyyyuna

感谢:https://github.com/lkeme/BiliHelper

感谢:https://github.com/czp3009/bilibili-api


本项目采用MIT开源协议
