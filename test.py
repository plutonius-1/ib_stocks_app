# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 15:44:51 2021

@author: avsha
"""

import pandas as pd

d1 = {"A":{"a":1,"b":2,"c":3,"d":4},
      "B":{"a":10,"b":20},
      "C":{"a":11,"b":22}}


df1 = pd.DataFrame.from_dict(d1)


def calc(df : pd.DataFrame):
    ser = df.loc["a"]
    print(ser)

    ser = ser[::-1]
    dic = {}
    
    div = len(ser)
    
    for idx in range(len(ser)):
        current_rnd_asset = 0.0
        for i in range(idx + 1):
            div = idx + 1
            current_rnd_asset += ser[i] * (i+1)/div
        dic.update({ser.index[idx]:current_rnd_asset})    
    
    res = pd.Series(dic)
    res = res[::-1]
    
    return res


calc(df1)