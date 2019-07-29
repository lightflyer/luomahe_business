# -*- coding:utf-8 -*-
import time

from commom.yima import YiMa, PROJECT_ID
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class EmailRegister(object):

    def __init__(self):
        self._sms_client = None
        self._sms_number = None

    # def set_sms_client(self):
    #     raise NotImplemented

    def receive_verify_sms(self):
        return self.sms_client.get_code(self.sms_number)

    @property
    def sms_number(self):
        if self._sms_number is None or not isinstance(self._sms_number, int):
            self._sms_number = self.sms_client.get_number()
        return self._sms_number

    @property
    def sms_client(self):
        if self._sms_client is None:
            self._sms_client = YiMa(PROJECT_ID.ProtonMail)
        return self._sms_client


class ProtonEmailRegister(EmailRegister):

    def __init__(self, user_name, user_pwd, recover_email, display_name):
        EmailRegister.__init__(self)
        opt = webdriver.ChromeOptions()
        # opt.add_argument('--no-sandbox')
        # opt.add_argument('headless')

        self.driver = webdriver.Chrome(chrome_options=opt)
        self.url = 'https://mail.protonmail.com/create/new?language=en'

        self.username = user_name
        self.user_pwd = user_pwd
        self.display_name = display_name
        self.recover_email = recover_email

    def open(self, timeout=30, poll_frequency=0.2):
        start_time = time.time()
        self.driver.get(url=self.url)
        # self.driver.find_element_by_class_name()
        # WebDriverWait(self.driver, timeout, poll_frequency).until(lambda x: x.find_element_by_name("submitBtn"))
        print(time.time() - start_time)
        time.sleep(10)
        print('hello world')
        # self.driver.find_element_by_id('username').send_keys(self.username)
        # self.driver.find_element_by_id('password').send_keys(self.user_pwd)
        # self.driver.find_element_by_id('passwordc').send_keys(self.user_pwd)
        # self.driver.find_element_by_id('notificationEmail').send_keys(self.recover_email)

        print(self.driver.page_source)
