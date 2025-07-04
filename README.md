# 说明
这是深圳大学自动抢羽毛球场脚本，包含预约、时间选择、添加同行人、支付的功能。
羽毛球场地是从还未被预约的场地中进行选择；支付是通过体育经费进行支付，运行前请确保体育经费充足。

# 配置
python环境配置详见requirements.txt，同时还要确保电脑有安装Google Chrome和Chromedriver,Chromedriver的下载地址 https://chromedriver.chromium.org/downloads。

注意Google Chrome和Chromedriver的版本需匹配。

# 运行
运行main.py前请新建config.py，复制以下代码信息填写   
```
CHROMEDRIVER_PATH = r"/opt/homebrew/bin/chromedriver"    # 需要填入自己电脑chromedriver的地址

xiaoqu = '粤海校区' #'丽湖校区'
sport_type = '羽毛球' # 运动类型，支持的运动类型有：羽毛球、乒乓球、网球、游泳
site = '羽毛球场'
index = 0 # 0代表当天预约，1代表明天预约，以此类推
appointment_time = "18:00-19:00(可预约)" # 预约按钮的文本
# 以下是必填的信息
username = "XXXXXXXXXX"             # 深圳大学统一认证的账号
password = "XXXXXXXXXX"             # 深圳大学统一认证的密码
appointment = 'XX:00-XX:00(可预约)'  # 想要预约的时间,格式为'XX:00-XX:00(可预约)',如'08:00-09:00(可预约)'或'18:00-19:00(可预约)'
payment_password = 'XXXXXXXXXX'     # 支付体育经费的密码
companions_id = ['XXXXXXXXXX']      # 同行人的校园卡号或学号，可填多个同行人，格式为['XXXXXXXXXX','XXXXXXXXXX',……]
```
填写完成后，脚本会一直运行，直到抢场完成才运行结束，若抢场成功，会显示“预约并支付成功”。  
