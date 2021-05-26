import defs
import requests
import pandas as pd
from pprint import pprint as pp

def align_date_format(x : str):
    dt = defs.datetime.strptime(x, defs.MARKETWATCH_DATE_FORMAT)
    alinged_date = dt.strftime(defs.IB_DATE_FORMAT)
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

def get_Q_data(ticker : str):

    r = pd.read_html("https://www.marketwatch.com/investing/stock/mmm/financials/income/quarter")
    if (len(r) < 5):
        print("No Data availabe from MarketWatch")
        return None

    df = r[4]

    # fix double spaces
    if ("  "  in df.columns[0]):
        tags = df[df.columns[0]]
        tags = tags.map(lambda x : x.split("  ")[0])
        tags = tags.str.lower()
        df[df.columns[0]] = tags

    # convert dates to match IB format
    df = align_df_dates(df)

    # TODO remove unnecsery "trend" column
    # TODO parse multiplers to be as same as IB - first find out where is IB definded - probably in the XML

    return df

df = get_Q_data("MMM")



