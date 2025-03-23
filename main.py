#%%
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service  # 添加Service导入
import schedule
import time
import sys

url = "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do?t_s=1709183352309#/sportVenue"
# url = "https://authserver.szu.edu.cn/authserver/login?service=https%3A%2F%2Fehall.szu.edu.cn%3A443%2Flogin%3Fservice%3Dhttps%3A%2F%2Fehall.szu.edu.cn%2Fnew%2Findex.html"
chromedriver = r"/opt/homebrew/bin/chromedriver"  # 需要填入自己电脑chromedriver的地址
service = Service(chromedriver)  # 创建Service对象
driver = webdriver.Chrome(service=service)  # 使用service参数

# 以下是必填的信息
username = ""  # 深圳大学统一认证的账号
password = ""  # 深圳大学统一认证的密码
appointment = "20:00-21:00(可预约)"  # 想要预约的时间,格式为'XX:00-XX:00(可预约)',如'08:00-09:00(可预约)'或'18:00-19:00(可预约)'
payment_password = "XXXXXXXXXX"  # 支付体育经费的密码
companions_id = [
    "XXXXXXXXXX"
]  # 同行人的校园卡号或学号，可填多个同行人，格式为['XXXXXXXXXX','XXXXXXXXXX',……]

# 获取当前日期
date = time.strftime("%Y-%m-%d", time.localtime())
# 获取明日日期
date = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))
#%%

def Login():
    """登录"""
    driver.get(url)
    driver.find_element(By.ID, "username").send_keys(username)
    time.sleep(2)
    driver.find_element(By.ID, "password").send_keys(password)
    # 更新为新的选择器方式
    driver.find_element(By.ID, "login_submit").click()


def Select():
    """选择时间并从可选的球场中选场"""

    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div[text()='粤海校区']"))
    )
    element.click()
    print("粤海校区")

    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//div[text()='羽毛球']"))
    )
    element.click()
    print("羽毛球")

    # wait = WebDriverWait(driver, 10)
    # element = wait.until(EC.visibility_of_element_located((By.XPATH, "/div[@class='ellipse-5']")))
    # element.click()
    # date_buttons = driver.find_elements(By.CSS_SELECTOR, ".group-9")
    max_iterations = 10000  # 设定最大迭代次数
    iteration = 0
    while iteration < max_iterations:
        print(f"第{iteration}次迭代")
        # 每次循环动态获取 date_buttons
        date_buttons = WebDriverWait(driver, 1).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".group-9"))
        )
        # 点击每个按钮
        for button in date_buttons:
            date_text = button.find_element(By.CSS_SELECTOR, ".text-wrapper-9").text
            button.click()
            try:
                element = WebDriverWait(driver, 1).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, f"//div[contains(text(),'{appointment}')]")  # 修复XPath表达式
                    )
                )
                if element:
                    element.click()
                    buttons = WebDriverWait(driver, 1).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, ".group-2")
                        )
                    )
                    print(buttons)

                    for button in buttons:
                        if (
                            (date_text == date)
                            and ("可预约" in button.text)
                            and ("羽毛球场" in button.text)
                        ):
                            print(button)
                            button.click()
                            break
                    element = WebDriverWait(driver, 1).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//button[text()='提交预约']")
                        )
                    )
                    element.click()
                    # 退出循环
                    print("预约成功")
                    return
            except Exception as e:
                print(f"{e}:当前日期{date_text}没有可预约的时间")
        iteration += 1  # 计数器增加

    buttons = driver.find_elements(By.CSS_SELECTOR, ".group-2")
    for button in buttons:
        if ("可预约" in button.text) and ("羽毛球场" in button.text):
            button.click()
            break

    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//button[text()='提交预约']"))
    )
    element.click()


def Add_companions():
    """添加同行人"""
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//a[text()='同行人']"))
    )
    element.click()

    for companion_id in companions_id:
        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//button[text()='添加同行人']")
            )
        )
        element.click()
        time.sleep(1)

        driver.find_element(By.ID, "searchId").send_keys(companion_id)
        driver.find_element(By.XPATH, "//div[text()='查询']").click()

        wait = WebDriverWait(driver, 10)
        element = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='确定']"))
        )
        element.click()

    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.CLASS_NAME, "jqx-window-close-button"))
    )
    element.click()


def Pay():
    """通过体育经费支付"""
    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//a[text()='未支付']"))
    )
    element.click()

    time.sleep(1)
    try:
        button = driver.find_element(By.XPATH, "//button[text()='(体育经费)支付']")
        button.click()
    except NoSuchElementException:
        button = driver.find_element(By.XPATH, "//button[text()='(剩余金额)支付']")
        button.click()
        return
    time.sleep(8)

    # 切换到支付窗口
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((By.ID, "btnNext")))
    element.click()

    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    element.click()

    time.sleep(1)
    for ele in payment_password:
        driver.find_element(By.CLASS_NAME, f"key-button.key-{ele}").click()

    wait = WebDriverWait(driver, 10)
    element = wait.until(
        EC.visibility_of_element_located((By.XPATH, "//button[text()='确认支付']"))
    )
    element.click()


def Work():
    Login()
    Select()
    # Add_companions()
    # Pay()
    # print("预约并支付成功")
    # sys.exit()


schedule.every().day.at("12:00").do(Work)  # 12:00自动开始预约

if __name__ == "__main__":
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    Work()
