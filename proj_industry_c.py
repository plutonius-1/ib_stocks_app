from proj_ticker_data_c import Ticker_data_c
from cfg import pd
import numpy as np
import cfg
import proj_utils

#### INDUSTRY OPERATIONS ####

def industry_op_avg_add(industy_avg, num_of_old_companies, new_val):
    return (industy_avg * num_of_old_companies + new_val) / (num_of_old_companies + 1)

def industry_op_avg_remove(industy_avg, num_of_old_companies, val_to_remove):
    return (industy_avg * num_of_old_companies - val_to_remove) / (num_of_old_companies - 1)

def industry_cumsum(**kwargs):
    add_remove = kwargs["add_remove"]
    val        = kwargs["val"]
    current_total = kwargs["current_total"]

    if (add_remove == "add"):
        return current_total + val
    else:
        return current_total - val

AVG_OP = "AVG_OP"
CUMSUM = "CUMSUM"

operations_based_on_data_type = {
    cfg.MKTCAP    : AVG_OP,
    cfg.VOL10DAVG : AVG_OP,
    cfg.EV        : AVG_OP,
    cfg.TTMREVPS  : AVG_OP,
    cfg.QBVPS     : AVG_OP,
    cfg.QCSHPS    : AVG_OP,
    cfg.TTMCFSHR  : AVG_OP,
    cfg.TTMDIVSHR : AVG_OP,
    cfg.TTMGROSMGN: AVG_OP,
    cfg.TTMROEPCT : AVG_OP,
    cfg.TTMPR2REV : AVG_OP,
    cfg.PEEXCLXOR : AVG_OP,
    cfg.PRICE2BK  : AVG_OP,
    cfg.MKTCAP_TOTAL : CUMSUM
}

operations_add_funcs = {
    AVG_OP : industry_op_avg_add,
    CUMSUM : industry_cumsum
}

operations_remove_funcs = {
    AVG_OP : industry_op_avg_remove,
    CUMSUM : industry_cumsum
}


class Industry_c:
    def __init__(self, industry_name, SIC):
        self.industry_name = industry_name
        self.SIC           = SIC
        self.tickers        = {}
        self.industry_data  = {}
        self.last_update    = cfg.DEFAULT_OBJECT_LAST_UPDATE

    def add_ticker_data(self, ticker, ticker_data):
        ticker_d = Ticker_data_c()
        ticker_d.set_ticker(ticker)

        # setting raw data also set the analzed data
        ticker_d.set_raw_data(ticker_data)
        for data_name in cfg.COMPARISON_PARAMS:
            ticker_d.set_in_indutry_avg(data_name, False)

        # in case ticker already exists in industry
        if (ticker in self.tickers):
            ticker_d = self._remove_tickers_data_from_industry_data(ticker_d)
        else:
            ticker_d = self._add_ticker_data_to_industry_data(ticker_d)

        # deal with the case that the ticker is already in the tickers{} dict - in this case remove the old data from the industry data and add the new
        self.tickers.update({ticker : ticker_d})

    def _get_add_remove_function(self,
                                 add_remove : str,
                                 data_name : str):
        if (data_name not in operations_based_on_data_type):
            return None

        if (add_remove == "add"): dic = operations_add_funcs
        else                   : dic = operations_remove_funcs

        return dic[operations_based_on_data_type[data_name]]



    def _remove_tickers_data_from_industry_data(self, new_ticker_obj : Ticker_data_c):
        ticker = new_ticker_obj.get_ticker()

        # first get old tickers data and compare to new data
        old_ticker_obj = self.industry_data[ticker]

        if (old_ticker_obj == new_ticker_obj):
            return
        else:
            old_analyzed_data = old_ticker_obj.get_analyzed_data()
            num_of_companies  = len(self.tickers)
            for data_name, val in old_analyzed_data.items():

                # get the func to do base on data name ("MKCAP, EV...")

                func_to_perform = self._get_add_remove_function("REMOVE", data_name)
                val_to_remove   = float(val)

                current_industry_val = float(self.industry_data[data_name])
                if func_to_perform == None:
                    proj_utils.print_warning_msg("{}: data name {} was not added to industry data".format(ticker, data_name))
                    new_ticker_obj.set_in_indutry_avg(data_name, False)
                else:
                    new_industry_val = func_to_perform(current_industry_val, num_of_companies, val_to_remove)
                    self.industry_data[data_name] = new_industry_val
                    new_ticker_obj.set_in_indutry_avg(data_name, True)

        return new_ticker_obj


    def _add_ticker_data_to_industry_data(self, new_ticker_obj : Ticker_data_c):
        new_analyzed_data = new_ticker_obj.get_analyzed_data()
        num_of_companies = len(self.tickers)

        # print(f"Adding ticker {new_ticker_obj}\n")
        for data_name, new_val in new_analyzed_data.items():

            func_to_perform = self._get_add_remove_function("add",data_name)
            new_val = float(new_val)

            if func_to_perform == None:
                proj_utils.print_warning_msg("{}: data name {} was not added to industry data".format(new_ticker_obj.get_ticker()
                                                                                                      , data_name))
                new_ticker_obj.set_in_indutry_avg(data_name, False)

            else:
                try:
                    current_industry_val = float(self.industry_data[data_name])
                except:
                    current_industry_val = 0.0

                new_industry_val = func_to_perform(current_industry_val, num_of_companies, new_val)
                self.industry_data[data_name] = new_industry_val
        return new_ticker_obj

    def get_industry_data(self):
        return self.industry_data

    def analyze_industry_after_tickers_are_added(self):
        MKTCAP_TOTAL_sum = 0.0

        # get the total market cap of the SIC
        for ticker_obj in self.tickers.values():
            try:
                MKTCAP_TOTAL_sum += float(ticker_obj.get_analyzed_data()[cfg.MKTCAP])
                # in case ticker does not have data from IB (grey stock for exmaple)
            except:
                pass
        self.industry_data.update({cfg.MKTCAP_TOTAL:MKTCAP_TOTAL_sum})

        # for each ticker add ranking for each of the tags
        for ticker_obj in self.tickers.values():

            ticker_obj_data = ticker_obj.get_analyzed_data()

            # add mktshare data
            try:
                mktshare = float(ticker_obj_data[cfg.MKTCAP]) / float(self.industry_data[cfg.MKTCAP_TOTAL])
                ticker_obj.add_data_to_analyzed_data(cfg.MKTSHARE, mktshare)
            except:
                pass


        # make df for all industries tickers vs their analyzed data
        # look like so:
            # ticker  : MKTCAP | 10DAVAVG | ...
            # --------------------------------------
            # ticker1 : ...
            # ticker2 : ...
        df = pd.DataFrame.from_dict(dict(zip(self.tickers, [i.get_analyzed_data() for i in self.tickers.values()])),orient = 'index')

        # sort for each param and get the index of each ticker after sorting
        df_params = df.columns
        for param in df_params:
            temp_df = df.sort_index()
            temp_df = temp_df.sort_values(param, ascending = True)
            ratings = dict(zip(temp_df.index, [i for i in range(len(temp_df.index))]))
            for ticker, tick_rating in ratings.items():
                self.tickers[ticker].add_data_to_analyzed_data(param + "_Rating", tick_rating)
        return

    def set_last_update(self):
        self.last_update = proj_utils.get_date()

    ## GETS ##
    def get_industry_as_df(self):
        df = pd.DataFrame.from_dict(dict(zip(self.tickers, [i.get_analyzed_data() for i in self.tickers.values()])),orient = 'index')
        return df

    def get_last_update(self):
        return self.last_update

    ## OVERRIDES ##
    def __repr__(self):
        return "Industry: {}({})\nNum of companies: {}\nTickers:{}".format(self.industry_name,
                                                                           self.SIC,
                                                                           len(self.tickers),
                                                                           [t for t in self.tickers])






