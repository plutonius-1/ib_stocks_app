def get_avg():
     avg = 0
     for name,ticker in ind.tickers.items():
             val = ticker.get_statements_df()["INC_Q"].loc["net income"][0]
             avg += val
     return avg / len(ind.tickers)# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 15:44:51 2021

@author: avsha
"""

import pandas as pd
import time
from datetime import datetime


import proj_series

data = pd.read_pickle("./SICS/dictionary.pkl")
ind  =data['4400']
CCL,MATX = ind.tickers["CCL"],ind.tickers["MATX"]
ccl_ser, matx_ser  = CCL.find_line_in_statements("non-cash items", "K"), MATX.find_line_in_statements("non-cash items","K")
CCL.analyze_data()
ind.analyze_industry_after_tickers_are_added()
print(ind.industry_period_data)



