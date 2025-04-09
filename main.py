# %%
import logging
import sys
import time
from datetime import datetime, timedelta

import requests
import schedule
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import *

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('badminton_booking.log')]
)
logger = logging.getLogger(__name__)

# 常量配置
URL = "https://ehall.szu.edu.cn/qljfwapp/sys/lwSzuCgyy/index.do?t_s=1709183352309#/sportVenue"

# 初始化WebDriver
def init_driver():
    """初始化并返回WebDriver实例"""
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        return driver
    except Exception as e:
        logger.error(f"WebDriver初始化失败: {e}")
        sys.exit(1)

# 获取日期信息
def get_date_info():
    """获取当前日期和明日日期"""
    today = time.strftime("%Y-%m-%d", time.localtime())
    tomorrow = time.strftime("%Y-%m-%d", time.localtime(time.time() + 86400))
    logger.info(f"当前日期：{today}, 明日日期：{tomorrow}")
    return today, tomorrow

def wait_for_element(driver, by, value, timeout=10, condition="visibility"):
    """等待并返回元素"""
    try:
        wait = WebDriverWait(driver, timeout)
        if condition == "visibility":
            element = wait.until(EC.visibility_of_element_located((by, value)))
        elif condition == "presence":
            element = wait.until(EC.presence_of_element_located((by, value)))
        elif condition == "clickable":
            element = wait.until(EC.element_to_be_clickable((by, value)))
        return element
    except TimeoutException:
        logger.warning(f"等待元素超时: {by}={value}")
        return None

def wait_for_elements(driver, by, value, timeout=10):
    """等待并返回多个元素"""
    try:
        wait = WebDriverWait(driver, timeout)
        elements = wait.until(EC.presence_of_all_elements_located((by, value)))
        return elements
    except TimeoutException:
        logger.warning(f"等待多个元素超时: {by}={value}")
        return []

def login(driver):
    """登录系统"""
    try:
        logger.info("开始登录")
        driver.get(URL)
        
        # 输入用户名和密码
        username_field = wait_for_element(driver, By.ID, "username")
        if username_field:
            username_field.send_keys(username)
            time.sleep(2)
        
        password_field = wait_for_element(driver, By.ID, "password")
        if password_field:
            password_field.send_keys(password)
            time.sleep(1)
        
        # 点击登录按钮
        login_button = wait_for_element(driver, By.ID, "login_submit", condition="clickable")
        if login_button:
            login_button.click()
            logger.info("登录请求已发送")
        else:
            logger.error("找不到登录按钮")
            return False
        
        # 检查登录成功
        if wait_for_element(driver, By.XPATH, "//div[text()='粤海校区']", timeout=20):
            logger.info("登录成功")
            return True
        else:
            logger.error("登录失败或超时")
            return False
    except Exception as e:
        logger.error(f"登录过程出错: {e}")
        return False

def select_venue_type(driver):
    """选择校区和运动类型"""
    try:
        # 选择粤海校区
        campus = wait_for_element(driver, By.XPATH, "//div[text()='粤海校区']", timeout=15)
        if campus:
            campus.click()
            logger.info("已选择粤海校区")
        else:
            logger.error("无法选择粤海校区")
            return False
            
        # 选择羽毛球
        sport = wait_for_element(driver, By.XPATH, "//div[text()='羽毛球']", timeout=10)
        if sport:
            sport.click()
            logger.info("已选择羽毛球")
            return True
        else:
            logger.error("无法选择羽毛球")
            return False
    except Exception as e:
        logger.error(f"选择场馆类型时出错: {e}")
        return False

def find_available_court(driver, appointment_time, tomorrow_date):
    """查找并选择可用的场地"""
    logger.info(f"开始查找时间段: {appointment_time}, 日期: {tomorrow_date}")
    time.sleep(2)   # 等待页面加载
    max_iterations = 10000  # 减少最大迭代次数以避免无限循环
    for iteration in range(max_iterations):
        logger.info(f"第{iteration + 1}次查找迭代")
        
        # 获取日期按钮
        date_buttons = wait_for_elements(driver, By.CSS_SELECTOR, ".group-9", timeout=5)
        if not date_buttons:
            logger.warning("没有找到日期按钮，重试中...")
            time.sleep(1)
            continue
        # 遍历每个日期按钮
        for button in date_buttons:
            try:
                date_text = button.find_element(By.CSS_SELECTOR, ".text-wrapper-9").text
                logger.info(f"检查日期: {date_text}")
                
                # 点击日期按钮
                button.click()
                time.sleep(0.5)
                if (date_text != tomorrow_date) :
                    continue
                # 尝试找到指定时间段
                try:
                    time_slot = wait_for_element(
                        driver, 
                        By.XPATH, 
                        f"//div[contains(text(),'{appointment_time}')]", 
                        timeout=1
                    )
                    if time_slot:
                        time_slot.click()
                        logger.info(f"选中时间段: {appointment_time}")
                        
                        # 查找可预约的场地
                        courts = wait_for_elements(driver, By.CSS_SELECTOR, ".group-2", timeout=2)
                        for court in courts:
                            court_text = court.text
                            if  ("可预约" in court_text) and ("羽毛球场" in court_text):
                                logger.info(f"找到可预约场地: {court_text}")
                                court.click()
                                
                                # 点击提交预约按钮
                                submit_btn = wait_for_element(
                                    driver, 
                                    By.XPATH, 
                                    "//button[text()='提交预约']",
                                    timeout=2,
                                    condition="visibility"
                                )
                                if submit_btn:
                                    submit_btn.click()
                                    logger.info("已点击提交预约按钮")
                                    return True
                                else:
                                    logger.warning("未找到提交预约按钮")
                except TimeoutException:
                    logger.info(f"日期 {date_text} 没有找到时间段 {appointment_time}")
            except Exception as e:
                logger.warning(f"处理日期按钮时出错: {e}")

    logger.warning(f"经过 {max_iterations} 次尝试后未找到可用场地")
    return False

def add_companions(driver):
    """添加同行人"""
    if not companions_id or len(companions_id[0]) == 0:
        logger.info("无需添加同行人")
        return True
        
    try:
        # 点击同行人标签
        companion_tab = wait_for_element(driver, By.CLASS_NAME, 'j-row-txr', timeout=10)
        if companion_tab:
            companion_tab.click()
            logger.info("点击了同行人标签")
        else:
            logger.error("未找到同行人标签")
            return False
        
        # 已经添加的同行人
        # 等待表格加载完成（显式等待）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tabledataTable"))
        )
        
        # 定位所有学号所在的<span>元素
        student_ids = driver.find_elements(By.XPATH, "//table[@id='tabledataTable']//tr/td[3]/span")
        
        # 提取学号文本并存入列表
        ids_list = [sid.text for sid in student_ids]
        print("学号列表:", ids_list)
        companions = set(ids_list)
        print(companions)
        # 添加每个同行人
        for companion_id in companions_id:
            # 如果已经添加过，则跳过
            if companion_id == username:
                logger.info(f"跳过自己的账号: {companion_id}")
                continue
            if companion_id in companions:
                logger.info(f"同行人 {companion_id} 已经添加")
                continue
            if not companion_id:
                continue
                
            # 点击添加同行人按钮
            add_button = wait_for_element(
                driver, 
                By.XPATH, 
                '//button[text()="添加同行人"]',
                timeout=10
            )
            if add_button:
                add_button.click()
                time.sleep(1)
            else:
                logger.error("未找到添加同行人按钮")
                continue
            
            # 输入同行人ID并查询
            id_field = wait_for_element(driver, By.ID, "searchId")
            if id_field:
                id_field.send_keys(companion_id)
                
                search_btn = wait_for_element(driver, By.XPATH, "//div[text()='查询']")
                if search_btn:
                    search_btn.click()
                    time.sleep(1)
                    
                    # 点击确定按钮
                    confirm_btn = wait_for_element(driver, By.XPATH, "//button[text()='确定']")
                    if confirm_btn:
                        confirm_btn.click()
                        logger.info(f"已添加同行人: {companion_id}")
                    else:
                        logger.warning(f"无法确认添加同行人: {companion_id}")
        
        # 关闭同行人窗口
        close_btn = wait_for_element(driver, By.XPATH, '//button[text()="关闭"]', timeout=10)
        if close_btn:
            close_btn.click()
            logger.info("已关闭同行人窗口")
            return True
        else:
            logger.warning("未找到关闭同行人窗口按钮")
            return False
    except Exception as e:
        logger.error(f"添加同行人时出错: {e}")
        return False

def make_payment(driver):
    """支付预约费用"""
    try:
        # 点击未支付标签
        unpaid_tab = wait_for_element(driver, By.XPATH, '//*[@id="row0myBookingInfosTable"]/td[1]/a[3]', timeout=10)
        if unpaid_tab:
            unpaid_tab.click()
            logger.info("进入支付界面")
        else:
            logger.error("未找到支付标签")
            return False
        
        time.sleep(2)
        
        # 尝试体育经费支付，如果失败则尝试剩余金额支付
        try:
            sports_fund_btn = wait_for_element(
                driver, 
                By.XPATH, 
                "//button[text()='(体育经费)支付']", 
                timeout=3
            )
            if sports_fund_btn:
                sports_fund_btn.click()
                logger.info("选择体育经费支付")
            else:
                logger.info("未找到体育经费支付按钮，尝试剩余金额支付")
                remainder_btn = wait_for_element(
                    driver, 
                    By.XPATH, 
                    "//button[text()='(剩余金额)支付']", 
                    timeout=3
                )
                if remainder_btn:
                    remainder_btn.click()
                    logger.info("选择剩余金额支付")
                    return True
                else:
                    logger.error("未找到任何支付方式按钮")
                    return False
        except Exception as e:
            logger.error(f"选择支付方式时出错: {e}")
            return False
            
        # 等待跳转到支付页面
        time.sleep(8)
        
        # 切换到支付窗口
        try:
            window_handles = driver.window_handles
            driver.switch_to.window(window_handles[-1])
            logger.info("切换到支付窗口")
        except Exception as e:
            logger.error(f"切换到支付窗口失败: {e}")
            return False
            
        # 点击下一步按钮
        next_btn = wait_for_element(driver, By.ID, "btnNext", timeout=10)
        if next_btn:
            next_btn.click()
            logger.info("点击下一步按钮")
        else:
            logger.error("未找到下一步按钮")
            return False
            
        # 点击密码框
        password_field = wait_for_element(driver, By.ID, "password", timeout=10)
        if password_field:
            password_field.click()
        else:
            logger.error("未找到密码输入框")
            return False
            
        # 输入支付密码
        time.sleep(1)
        for digit in payment_password:
            digit_btn = wait_for_element(driver, By.CLASS_NAME, f"key-button.key-{digit}", timeout=2)
            if digit_btn:
                digit_btn.click()
            else:
                logger.error(f"未找到数字键 {digit}")
                return False
        
        logger.info("已输入支付密码")
        # 确定按钮
        queding_btn = wait_for_element(driver, By.XPATH, '//*[@id="keybox"]/table/tbody/tr[2]/td[6]/input', timeout=10)
        if queding_btn:
            queding_btn.click()
            logger.info("点击确定按钮")
        else:
            logger.error("未找到确定按钮")
            return False
        # 确认支付
        confirm_btn = wait_for_element(
            driver, 
            By.XPATH, 
            "//button[text()='确认支付']", 
            timeout=10
        )
        if confirm_btn:
            confirm_btn.click()
            logger.info("确认支付")
            time.sleep(3)  # 等待支付完成
            return True
        else:
            logger.error("未找到确认支付按钮")
            return False
    except Exception as e:
        logger.error(f"支付过程出错: {e}")
        return False

def booking_workflow():
    """执行完整的预约流程"""
    driver = init_driver()
    date = get_date_info()
    
    try:
        # 登录系统
        if not login(driver):
            logger.error("登录失败，终止流程")
            return False
            
        # 选择场馆类型
        if not select_venue_type(driver):
            logger.error("选择场馆类型失败，终止流程")
            return False
            
        # 寻找可用场地
        if not find_available_court(driver, appointment_time,date[index]):
            logger.error("未找到可用场地，终止流程")
            return False
        logger.info("预约提交成功，准备添加同行人和支付")

        # # 选择我的预约
        # my_booking = wait_for_element(driver, By.XPATH, '/html/body/header/header[1]/div/div/div[4]/div[4]/a[3]/div')
        # if my_booking:
        #     my_booking.click()
        #     logger.info("点击我的预约")
        # else:
        #     logger.error("未找到我的预约")
        #     return False
            
        
        # 添加同行人（如果需要）
        if companions_id and len(companions_id[0]) > 0:
            if not add_companions(driver):
                logger.warning("添加同行人失败，但将继续执行")
        
        # 支付流程
        if not make_payment(driver):
            logger.error("支付失败")
            return False
            
        logger.info("预约和支付全部完成")
        return True
    except Exception as e:
        logger.error(f"预约流程中出现未处理异常: {e}")
        return False
    finally:
        try:
            driver.quit()
            logger.info("已关闭浏览器")
        except:
            pass

if __name__ == "__main__":
    # 每天中午12点执行预约
    schedule.every().day.at("12:00").do(booking_workflow)
    # 直接执行一次预约流程
    booking_workflow()
