# -*- coding: UTF-8 -*-
# 思路：利用selenium+chromedriver来实现
# 1、让浏览器（chrome）打开12306的登录界面，然后手动进行登陆
# 2、登录完成后让浏览器跳转到购票的界面
# 3、手动的输入出发地，目的地以及出发日期，检测到以上三个信息都输入完成后，然后找到查询按钮，执行点击事件，进行车次查询
# 4、查找我们需要的车次，然后看下对应的席位是否还有余票（有、数字）。找到这个车次的预订按钮，然后执行点击事件。如果没有出现以上两个（有数字），那么我们就循环这个查询工作。
# 5、一旦检测到有票（有、数字），那么执行预定按钮的点击事件，来到预定的界面后，找到对应的乘客，然后执行这个乘客的checkbox，然后执行点击事件，再找到提交按钮，执行点击事件。
# 6、点击完提交订单按钮以后，会弹出一个确认的对话框，然后找到“确认按钮”，然后执行点击事件，这样就完成了抢票。

# 导入包
import time
import random

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class QianPiao(object):
    def __init__(self):
        # 用户前期输入内容
        self.from_station = input("请输入出发地：")
        self.to_station = input("请输入目的地：")
        self.depart_time = input("出发时间（格式yyyy-mm-dd）：")
        self.passengers = input("乘客姓名（如有多个乘客，用英文逗号隔开）：").split(",")
        self.trans = input("车次（如有多个车次，用英文逗号隔开）：").split(",")

        # 登录界面url
        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        # 登录成功界面的url
        self.initmy_url = "https://kyfw.12306.cn/otn/view/index.html"
        # 订票界面的url
        self.search_url = "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc"
        # 订票乘客确认界面的url
        self.passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        # 实例化一个配置对象
        self.driver = webdriver.Chrome()

    # 登录操作
    def _login(self):
        self.driver.get(self.login_url)
        # 显示等待
        WebDriverWait(self.driver, 1000, 1).until(
            EC.url_to_be(self.initmy_url)
        )
        print('登陆成功')

    # 订票操作
    def _order_tickket(self):
        # 1、跳转到订票页面
        self.driver.get(self.search_url)
        # 2、等待验证页面输入信息是否正确
        WebDriverWait(self.driver, 1000, 1).until(
            EC.text_to_be_present_in_element_value((By.ID, "fromStationText"), self.from_station)
        )
        WebDriverWait(self.driver, 1000, 1).until(
            EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_station)
        )
        WebDriverWait(self.driver, 1000, 1).until(
            EC.text_to_be_present_in_element_value((By.ID, "train_date"), self.depart_time)
        )
        # 3、等待查询按钮是否可用
        WebDriverWait(self.driver, 1000, 1).until(
            EC.element_to_be_clickable((By.ID, "query_ticket"))
        )
        # 4、如果查询按钮能够被点击，那就找到这个查询按钮，执行点击事件
        searchBtn = self.driver.find_element(By.ID, "query_ticket")
        time.sleep(1)
        searchBtn.click()
        # 5、点击查询按钮后，等待查询车票结果显示出来
        WebDriverWait(self.driver, 1000, 1).until(
            EC.presence_of_element_located((By.XPATH, "//tbody[@id='queryLeftTable']/tr"))
        )
        # 6、找到所有没有datatran属性的tr标签，这些标签内存储了车次信息
        tr_list = self.driver.find_elements(By.XPATH, "//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
        # 7、遍历所有满足条件的tr标签
        for tr in tr_list:
            train_number = tr.find_element(By.CLASS_NAME, "number").text
            if train_number in self.trans:
                # 找到二等座车票信息的位置
                second_ticket = tr.find_element(By.XPATH, ".//td[4]").text
                # 如果暂时无票，开始抢票，循环不停的刷新余票
                count = 1
                while second_ticket == "无" or second_ticket == "--" or second_ticket == "候补":
                    print("暂无余票，正在尝试第%s次抢票···" % count)
                    time.sleep(random.randint(300, 1000))
                    time.sleep(1)
                    searchBtn.click()
                    count += 1
                # 判断输入的车次在列表中是否有票（显示有或者数字）
                if second_ticket == "有" or second_ticket.isdigit:
                    # 如果有票，找到预订按钮，然后点击预订按钮
                    orderBtn = tr.find_element(By.CLASS_NAME, "btn72")
                    time.sleep(1)
                    orderBtn.click()
                    # 等待是否来到确认乘客的页面
                    WebDriverWait(self.driver, 1000, 1).until(
                        EC.url_to_be(self.passenger_url)
                    )
                    # 等待乘客信息是否全部载入
                    WebDriverWait(self.driver, 1000, 1).until(
                        EC.presence_of_element_located((By.XPATH, ".//ul[@id = 'normal_passenger_id']/li"))
                    )
                    # 遍历所有的乘客列表
                    passanger_list = self.driver.find_elements(By.XPATH, ".//ul[@id = 'normal_passenger_id']/li/label")
                    for passanger in passanger_list:
                        name = passanger.text
                        # 判断输入的乘客姓名是否在列表中,如果存在则点击添加进乘客信息
                        if name in self.passengers:
                            time.sleep(1)
                            passanger.click()
                    # 乘客信息添加完成后，找到提交订单按钮，然后点击提交订单
                    submitBtn = self.driver.find_element(By.ID, "submitOrder_id")
                    time.sleep(1)
                    submitBtn.click()
                    # 等待订单确认界面全部载入
                    WebDriverWait(self.driver, 1000, 1).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "dhtmlx_wins_body_outer"))
                    )
                    # 等待确认按钮是否可用
                    WebDriverWait(self.driver, 1000, 1).until(
                        EC.element_to_be_clickable((By.ID, "qr_submit_id"))
                    )
                    # 如果确认按钮可以被点击，那就找到这个确认按钮，执行点击事件
                    conBtn = self.driver.find_element(By.ID, "qr_submit_id")
                    time.sleep(1)
                    conBtn.click()
                    # 最后手动进行支付工作
                    print("车票预订成功，请手动完成支付！")
                    print("系统正常退出······")
                    exit()

    # 运行函数
    def run(self):
        self._login()
        self._order_tickket()


if __name__ == '__main__':
    spider = QianPiao()
    spider.run()
