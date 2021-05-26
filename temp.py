import pandas as pd
import operator as op

data = {"A":[1,2,3], "B": [10,20,30]}

df = pd.DataFrame.from_dict(data)

def find_series_and_calc(df,
                         base_series : pd.Series,
                         tags : list,
                         operations : list,
                         transformations : list):

    assert len(tags) == len(operations) and len(transformations) == len(tags), "ERR"
    res = base_series

    for idx, tag in enumerate(tags):
        try:
            temp_series = df.loc[tag].fillna(0)
            op          = operations[idx]
            trans       = transformations[idx]
            if trans != None:
                temp_series = trans(temp_series)
            res         = op(res, temp_series)

        except:
            pass

    return res


print(find_series_and_calc(df = df,
                           base_series = df.loc[0],
                           tags = [0,1],
                           operations = [op.add, op.add],
                           transformations = [None, None]))
