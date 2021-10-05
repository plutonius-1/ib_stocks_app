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



