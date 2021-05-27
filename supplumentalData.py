import defs
import re
import requests
import pandas as pd
from pprint import pprint as pp

#####################################
### CONSTS ###
#####################################

MARKETWATCH_K_INCOME  = "https://www.marketwatch.com/investing/stock/{}/financials/income"
MARKETWATCH_K_BALANCE = "https://www.marketwatch.com/investing/stock/{}/financials/balance-sheet"
MARKETWATCH_K_CASH    = "https://www.marketwatch.com/investing/stock/{}/financials/cash-flow"
MARKETWATCH_Q_INCOME  = MARKETWATCH_K_INCOME + "/quarter/"
MARKETWATCH_Q_BALANCE = MARKETWATCH_K_BALANCE + "/quarter/"
MARKETWATCH_Q_CASH    = MARKETWATCH_K_CASH + "/quarter/"

def align_date_format(x : str):
    try:
        dt = defs.datetime.strptime(x, defs.MARKETWATCH_DATE_FORMAT)
        alinged_date = dt.strftime(defs.IB_DATE_FORMAT)
    except:
        if (x.isnumeric() and len(x) == 4): # i.e only year (2018 ...)
            x = x + "-12-31"
            alinged_date = x
        else:
            print("date if off format : given date = {}".format(x))
            return None

    return alinged_date

def align_df_dates(df):

    cols = df.columns
    new_cols = []
    for i in cols:
        try:
            new_i = align_date_format(i)
            new_cols.append(new_i)

        except:
            new_cols.append(i)
    df.columns = new_cols
    return df



def get_statement_data(addr : str):

    r = pd.read_html(addr)
    assert len(r) >= 5, "response from {} is not OK, length of reponse = {}".format(addr, len(r))
    relevant_dfs = []

    for temp_df in r:
        for col_name in temp_df.columns:
            if ("Item" in str(col_name)):
                relevant_dfs.append(temp_df)
    assert len(relevant_dfs) > 0, "Didn't find any DataFrames with relevant statement info"

    df = pd.concat(relevant_dfs)
    df.index = df[df.columns[0]]

    # fix double spaces
    if ("  "  in df.columns[0]):
        tags = df[df.columns[0]]
        tags = tags.map(lambda x : x.split("  ")[0])
        tags = tags.str.lower()
        df[df.columns[0]] = tags

    # convert dates to match IB format
    df = align_df_dates(df)

    # remove unnecsery "trend" column
    # assume columns 1:... should all be dates in coulms names
    # first chagne coumns 0 name to TAGS
    df.columns = ["tags"] + list(df.columns[1:])
    df  = df.dropna(
            axis = 1, # drop columns
            how = "all"
                    )


    for c in df.columns[1:]:
        match = re.search(r"[a-z]",str(c))
        if match:
            print("match for ", c)
            df = df.drop(labels = c, axis = 1)



    # TODO parse multiplers to be as same as IB - first find out where is IB definded - probably in the XML
    #df.index = df[df.columns[0]]
    return df

def get_period_data(
        ticker : str,
        period : str):

    if (period == "K"):
        inc_addr = MARKETWATCH_K_INCOME.format(ticker)
        bal_addr = MARKETWATCH_K_BALANCE.format(ticker)
        cas_addr = MARKETWATCH_K_CASH.format(ticker)
    else:
        inc_addr = MARKETWATCH_Q_INCOME.format(ticker)
        bal_addr = MARKETWATCH_Q_BALANCE.format(ticker)
        cas_addr = MARKETWATCH_Q_CASH.format(ticker)

    inc_df = get_statement_data(inc_addr)
    bal_df = get_statement_data(bal_addr)
    cas_df = get_statement_data(cas_addr)


    return {"INC" : inc_df.to_dict(), "BAL" : bal_df.to_dict(), "CAS" : cas_df.to_dict()}

def get_data(ticker : str):

    k_data = get_period_data(ticker = ticker, period = "K")
    q_data = get_period_data(ticker = ticker, period = "Q")

    return {"Q_data" : q_data, "K_data" : k_data}






