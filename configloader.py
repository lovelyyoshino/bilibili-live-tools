import configparser
import webcolors
import codecs
import toml


# "#969696"
def hex_to_rgb_percent(hex_str):
    color = webcolors.hex_to_rgb_percent(hex_str)
    
    return [float(i.strip('%'))/100.0 for i in color]


# "255 255 255"
def rgb_to_percent(rgb_list):
    # print(rgb_list)
    color = webcolors.rgb_to_rgb_percent(rgb_list)
    
    return [float(i.strip('%'))/100.0 for i in color]

    
def load_bilibili(file):
    with open(file, encoding="utf-8") as f:
        dic_bilibili = toml.load(f)
    if dic_bilibili['account']['username']:
        pass
    else:
        username = input("# 输入帐号: ")
        password = input("# 输入密码: ")
        dic_bilibili['account']['username'] = username
        dic_bilibili['account']['password'] = password
        with open(file, 'w',encoding="utf-8") as f:
            toml.dump(dic_bilibili, f)    
            
    return dic_bilibili
    
    
def load_color(file):
    with open(file, encoding="utf-8") as f:
        dic_color = toml.load(f)
    for i in dic_color.values():
        for j in i.keys():
            if isinstance(i[j], str):
                i[j] = hex_to_rgb_percent(i[j])
            else:
                i[j] = rgb_to_percent(i[j])
                    
    return dic_color
 
               
def load_user(file):
    with open(file, encoding="utf-8") as f:
        dic_user = toml.load(f)
    '''
    dictionary = {
            'user': 0,
            'debug': 1
        }
        之后抛弃
    '''    
    
    # print(dic_user)
            
    return dic_user
    
    
class ConfigLoader():
    
    instance = None

    def __new__(cls, colorfile=None, userfile=None, bilibilifile=None):
        if not cls.instance:
            cls.instance = super(ConfigLoader, cls).__new__(cls)
            cls.instance.colorfile = colorfile
            cls.instance.dic_color = load_color(colorfile)
            # print(cls.instance.dic_color)
            
            cls.instance.userfile = userfile
            cls.instance.dic_user = load_user(userfile)
            # print(cls.instance.dic_user)
            
            cls.instance.bilibilifile = bilibilifile
            cls.instance.dic_bilibili = load_bilibili(bilibilifile)
            # print(cls.instance.dic_bilibili)
            print("# 初始化完成")
        return cls.instance
    
    def write2bilibili(self, dic):
        # print(dic)
        with open(self.bilibilifile, encoding="utf-8") as f:
            dic_bilibili = toml.load(f)
        for i in dic.keys():
            dic_bilibili['saved-session'][i] = dic[i]
        with open(self.bilibilifile, 'w',encoding="utf-8") as f:
            toml.dump(dic_bilibili, f)
        
        

    
    
        
        
            
       
        


