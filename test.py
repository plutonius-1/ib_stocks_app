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


