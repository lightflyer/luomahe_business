# -*- coding:utf-8 -*-
from commom.yima import YiMa, PROJECT_ID


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
    pass
