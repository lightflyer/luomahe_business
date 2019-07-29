# -*- coding:utf-8 -*-
import unittest
from auto_register_protonmail import ProtonEmailRegister


class ProtonMailTest(unittest.TestCase):
    name = 'chuantest1'
    pwd = 'chuantest'
    display_name = 'chuantest'
    email = '280335444@qq.com'

    register = ProtonEmailRegister(user_name=name, user_pwd=pwd, recover_email=email, display_name=display_name)

    def test_open(self):
        self.register.open()
