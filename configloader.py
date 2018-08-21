import webcolors
import toml


# "#969696"
def hex_to_rgb_percent(hex_str):
    color = webcolors.hex_to_rgb_percent(hex_str)
    return [float(i.strip('%'))/100.0 for i in color]


# "255 255 255"
def rgb_to_percent(rgb_list):
    color = webcolors.rgb_to_rgb_percent(rgb_list)
    return [float(i.strip('%'))/100.0 for i in color]
    
    
class ConfigLoader():
    
    instance = None

    def __new__(cls, fileDir=None):
        if not cls.instance:
            cls.instance = super(ConfigLoader, cls).__new__(cls)
            
            colorfile = f'{fileDir}/conf/color.toml'
            userfile = f'{fileDir}/conf/user.toml'
            bilibilifile = f'{fileDir}/conf/bilibili.toml'
            titlefile = f'{fileDir}/conf/title.toml'
            
            cls.instance.colorfile = colorfile
            cls.instance.dic_color = cls.instance.load_color()
            # print(cls.instance.dic_color)
            
            cls.instance.userfile = userfile
            cls.instance.dic_user = cls.instance.load_user()
            # print(cls.instance.dic_user)
            
            cls.instance.bilibilifile = bilibilifile
            cls.instance.dic_bilibili = cls.instance.load_bilibili()
            # print(cls.instance.dic_bilibili)
            
            cls.instance.titlefile = titlefile
            cls.instance.dic_title = cls.instance.load_title()
            print("# 初始化完成")
        return cls.instance
    
    def write2bilibili(self, dic):
        with open(self.bilibilifile, encoding="utf-8") as f:
            dic_bilibili = toml.load(f)
        for i in dic.keys():
            dic_bilibili['saved-session'][i] = dic[i]
        with open(self.bilibilifile, 'w', encoding="utf-8") as f:
            toml.dump(dic_bilibili, f)
            
    def load_bilibili(self):
        with open(self.bilibilifile, encoding="utf-8") as f:
            dic_bilibili = toml.load(f)
        if not dic_bilibili['account']['username']:
            username = input("# 输入帐号: ")
            password = input("# 输入密码: ")
            dic_bilibili['account']['username'] = username
            dic_bilibili['account']['password'] = password
            with open(self.bilibilifile, 'w', encoding="utf-8") as f:
                toml.dump(dic_bilibili, f)
                
        return dic_bilibili
                
    def load_color(self):
        with open(self.colorfile, encoding="utf-8") as f:
            dic_color = toml.load(f)
        for i in dic_color.values():
            for j in i.keys():
                if isinstance(i[j], str):
                    i[j] = hex_to_rgb_percent(i[j])
                else:
                    i[j] = rgb_to_percent(i[j])
                        
        return dic_color
                        
    def load_user(self):
        with open(self.userfile, encoding="utf-8") as f:
            dic_user = toml.load(f)
        return dic_user
        
    def load_title(self):
        with open(self.titlefile, encoding="utf-8") as f:
            dic_title = toml.load(f)
        return dic_title
        

    
    
        
        
            
       
        


