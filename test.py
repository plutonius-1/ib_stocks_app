# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 15:44:51 2021

@author: avsha
"""

import pandas as pd
import time
from datetime import datetime


class my_c:
    def __init__(self):
        self.TIME_INC = 10
        self._last_timestamp = datetime.now()
        self.done = False

    def time_elapsed(self):
        now = datetime.now()
        return (now - self._last_timestamp).seconds

    def _update_last_timesamp(self, datetime_obj):
        self._last_timestamp = datetime_obj

    def update_counter(self, time_inc : int):
        while not self.did_enough_time_pased():
            print("not enought time passed")
            time.sleep(3)
        self._update_last_timesamp(datetime.now())

    def did_enough_time_pased(self):
        if (self.time_elapsed() > self.TIME_INC):
            return True
        return False

    def set_done(self, val : bool):
        self.done = val






class time_req_mgmt:
    def __init__(self):
        self._last_timestamp     = None
        self._last_req_timestamp = None
        self._halt_reqs = False
        self.PACING_TIME = 10
        self.max_reqs = 50
        self.req_counter = self.max_reqs

    def time_elapsed(self):
        return (self._last_req_timestamp - self._last_timestamp).seconds

    def did_enough_time_passed(self):
        return self.time_elapsed > self.PACING_TIME

    def do_req(self):
        self.req_counter -= 1
        self._last_req_timestamp = datetime.now()
        if (self._last_timestamp == None):
            self._last_timestamp = self._last_req_timestamp
        # TODO
        pass

    def make_req(self):
        if self.did_enough_time_passed:
            self._last_timestamp == None
            self.do_req()
        elif (not self.did_enough_time_passed) and (self.req_counter > 1):
            self.do_req()
        elif (self.did_enough_time_passed == False) and (self.req_counter <= 1):
            while not self.did_enough_time_passed:
                time.sleep(60)
                self._last_timestamp == None
                self.do_req()




    options:
        1) enough time passed - make req
        2) not enough time passed + under 50 reqs - make req
        3) not enough time passed + reached 50 - wait until 10  mins pass - make req







