# -*- coding:utf-8 -*-
import time

from commom.yima import YiMa, PROJECT_ID, ERROR_CODE
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from commom.protonmail_variables import SIGNUPELEMENTS as variables

class EmailRegister(object):

    def __init__(self):
        self._sms_client = None
        self._sms_number = None

    # def set_sms_client(self):
    #     raise NotImplemented

    def receive_verify_sms(self):
        res, code = self.sms_client.get_code(PROJECT_ID.ProtonMail, self.sms_number)
        if res == 0:
            return code
        else:
            raise Exception('get phone verified code error: {},reason:{}, content:{}'.format(res,
                                                                                             ERROR_CODE.get(
                                                                                                 int(res), None),
                                                                                             code))

    @property
    def sms_number(self):
        if self._sms_number is None or not isinstance(self._sms_number, int):
            res, number = self.sms_client.get_number(PROJECT_ID.ProtonMail)
            if res != 0:
                e_info = 'Encountered an error when get yima phone number:{}'.format(number)
                raise Exception(e_info)
            print('get mobile:{}'.format(number))
            self._sms_number = int(number)
        return str(self._sms_number)

    @property
    def sms_client(self):
        if self._sms_client is None:
            self._sms_client = YiMa()
            res, info = self._sms_client.get_account_info()
            if res != 0:
                raise Exception('Encountered an error when get yima account info :\n{}'.format(res))
        return self._sms_client


class ProtonEmailRegister(EmailRegister):

    def __init__(self, user_name, user_pwd, recover_email, display_name):
        EmailRegister.__init__(self)
        opt = webdriver.ChromeOptions()
        # opt.add_argument('--no-sandbox')
        # opt.add_argument('headless')

        self.driver = webdriver.Chrome(chrome_options=opt)

        # self.driver = webdriver.Firefox()
        self.url = 'https://mail.protonmail.com/create/new?language=en'

        self.username = user_name
        self.user_pwd = user_pwd
        self.display_name = display_name
        self.recover_email = recover_email

    def open(self, timeout=60, poll_frequency=0.2):
        start_time = time.time()
        self.driver.get(url=self.url)

        WebDriverWait(self.driver, timeout, poll_frequency).until(lambda x: x.find_element_by_tag_name(variables.iframe_tag))
        iframe_elements = self.driver.find_elements_by_tag_name(variables.iframe_tag)
        time.sleep(1)
        try:
            WebDriverWait(self.driver, timeout, poll_frequency)\
                .until(lambda x: x.find_element_by_tag_name(variables.iframe_tag))
            self.driver.switch_to.frame(iframe_elements[0])

            WebDriverWait(self.driver, timeout, poll_frequency)\
                .until(lambda x: x.find_element_by_id(variables.username_id))
            self.driver.find_element_by_id(variables.username_id).send_keys(self.username)
        except Exception as e:
            print('load page timeout, reason:{}'.format(e))
            return False, e
        # check if username is available
        try:
            WebDriverWait(self.driver, timeout, poll_frequency)\
                .until(lambda x: x.find_element_by_class_name(variables.username_available))
        except Exception as e:
            print('username has been used!!!')
            return False, e

        self.driver.switch_to.default_content()
        self.driver.find_element_by_name(variables.password_name).send_keys(self.user_pwd)
        time.sleep(1)
        self.driver.find_element_by_name(variables.passwordc_name).send_keys(self.user_pwd)
        time.sleep(1)
        self.driver.switch_to.frame(iframe_elements[1])
        self.driver.find_element_by_id(variables.notification_email_id).send_keys(self.recover_email)


        self.driver.find_element_by_name(variables.submit_btn_name).click()


        # WebDriverWait(self.driver, timeout, poll_frequency)\
        #     .until(lambda x: x.find_element_by_id(variables.sms_radio_id))

        time.sleep(5)
        print(self.driver.page_source)
        js = "document.getElementById('{}').style.display='block';".format(variables.sms_radio_id)
        self.driver.execute_script(js)

        self.driver.find_element_by_id(variables.sms_radio_id).click()

        time.sleep(2)
        self.driver.find_element_by_class_name(variables.country_class).click()
        time.sleep(1)
        self.driver.find_element_by_xpath(variables.china_xpath).click()
        # selector = Select(self.driver.find_element_by_class_name("country-list"))
        # for item in selector.options:
        #     print(item)
        phone = self.sms_number
        self.driver.find_element_by_name(variables.phone_input_name).send_keys(phone)

        self.driver.find_element_by_xpath(variables.sms_send_btn).click()

        verify_code = self.receive_verify_sms()
        print('号码为：{}, 验证码为：{}'.format(phone, verify_code))
        self.driver.find_element_by_id(variables.code_input_id).send_keys(verify_code)

        self.driver.find_element_by_xpath(variables.setup_btn_xpath).click()

        print(time.time() - start_time)

        print(self.driver.page_source)

    # def fill_info(self, timeout=30, poll_frequency=0.2):
    #     start_time = time.time()
    #     self.driver.get(url=self.url)
    #
    #     iframe_elements = self.driver.find_elements_by_tag_name(variables.iframe_tag)
    #
    #     WebDriverWait(self.driver, timeout, poll_frequency) \
    #         .until(lambda x: x.find_element_by_tag_name(variables.iframe_tag))
    #     self.driver.switch_to.frame(iframe_elements[0])
    #     #
    #     WebDriverWait(self.driver, timeout, poll_frequency).until(lambda x: x.find_element_by_id(variables.username_id))
    #     self.driver.find_element_by_id(variables.username_id).send_keys(self.username)
    #
    #     self.driver.switch_to.default_content()
    #     self.driver.find_element_by_name(variables.password_name).send_keys(self.user_pwd)
    #     self.driver.find_element_by_name(variables.passwordc_name).send_keys(self.user_pwd)
    #
    #     self.driver.switch_to.frame(iframe_elements[1])
    #     self.driver.find_element_by_id(variables.notification_email_id).send_keys(self.recover_email)
    #     self.driver.find_element_by_name(variables.submit_btn_name).click()
    #
    #     print(time.time() - start_time)
    #
    #     print(self.driver.page_source)

    def stop(self):
        self.driver.quit()
