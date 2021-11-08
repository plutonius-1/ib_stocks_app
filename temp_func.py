import pandas as pd
from test import *
def calc_relative(tick_s, base_s):
    assert len(tick_s) == len(base_s)

    res = tick_s

    for i in range(len(tick_s)):
        tick_val = tick_s[i]
        base_val = base_s[i]

        if ((tick_val > 0) and (base_val > 0)):
            res[i] = tick_val/base_val

        elif ((tick_val < 0) and (base_val < 0)):
            if (tick_val > base_val):
                res[i] = (1/tick_val)/(1/base_val)
            elif (tick_val < base_val):
                res[i] = -1 * (tick_val/base_val)
            else:
                res[i] = 1

        else:
            dist = abs(tick_val) + abs(base_val)
            temp_res = dist / abs(base_val)
            if ((tick_val < 0) and (base_val > 0)):
                temp_res *= -1
            res[i] = temp_res

    return res

ccl = ind.tickers["CCL"]
ccl_rev = ccl.get_pct_change_period_data()["IB"]["INC_Q"].get_data().loc["revenue"]
avg_rev = ind.industry_pct_change_data["IB"]["INC_Q"].get_data().loc["revenue"]
print(ccl_rev)
print(avg_rev)
print(calc_relative(ccl_rev, avg_rev))
