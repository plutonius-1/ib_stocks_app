import cfg
import proj_utils
from cfg import pd
from proj_ticker_data_c_v2 import Ticker_data_c
from base_data_obj_c import Base_data_obj_c

class Industry_data_obj_c(Base_data_obj_c):
    def __init__(self):
        self._name = "industry_data"
        self.tickers_data = {} # by sources

    def add_ticker_data(self):
        pass

    def get_ticker_data(self):
        pass


class Industry_c:
    def __init__(self, industry_name, SIC):
        self.industry_name = industry_name
        self.SIC           = SIC
        self.tickers        = {}
        self.industry_data  = {cfg.TICKERS : {},
                               cfg.MKTCAP_TOTAL : 0}    # initilize with empty tickers_dic -holds each tickers ranks and other comperative data
        self.industry_avg_data = {}
        self.industry_period_data = {cfg.K : {},
                                    cfg.Q : {}} # {K : yearly data,  Q : quarter data}
        self.last_update    = cfg.DEFAULT_OBJECT_LAST_UPDATE


    ## Main Funciton Runs ##

    def add_ticker_data(self, ticker, ticker_data, source):
        ticker_d = Ticker_data_c()
        ticker_d.set_ticker(ticker)
        ticker_d.set_raw_data(ticker_data, source)
        ticker_d.set_raw_statements()
        ticker_d.make_analyzed_data()
        ticker_d.set_pct_change_data()
        self.tickers.update({ticker : ticker_d})

    def calc_after_tickers_added(self):

        # update industry total market share
        self.industry_data[cfg.MKTCAP_TOTAL] = self._calc_industry_total_mktshare()

        # update tickers norm market share
        self._add_mktshare_data_to_tickers()

        # process data after all tickers added
        self.calc_ranking_data()

    ## Gets ##

    def get_companies_by_market_cap(self):
        #TODO
        return
    def get_last_update(self):
        return self.last_update

    ## General Use ##
    def _calc_industry_weighted_avg(self):
        """
        add tickers data of specific field to the industryh weighted avg,
        Note - This can only be done AFTER adding all the tickers to the industy.tickers.
        This means that every time we estimate a ticker, we need to delete the current data in the di        citonary of the SIC and refresh all that SICs data
        """

        # calc sum(w_i * x_i) - no need to devide by sum(w_i) since it is normilsed
        norm_avg = 0.0

        for ticker in self.tickers:
            ticker_analyzed_data = ticker.get_analyzed_data()
            w_i = ticker_analyzed_data[cfg.MKTSHARE]
        #x_tag =

        return None

    def _sub_from_industy_weighted_avg(self):

        return None

    def _calc_industry_total_mktshare(self):
        MKTCAP_TOTAL_sum = 0.0

        # get the total market cap of the SIC
        for ticker_obj in self.tickers.values():
            try:
                MKTCAP_TOTAL_sum += float(proj_utils._finditem(ticker_obj.get_analyzed_data(),cfg.MKTCAP))
                # in case ticker does not have data from IB (grey stock for exmaple)
            except:
                pass
        return MKTCAP_TOTAL_sum

    def _add_mktshare_data_to_tickers(self):
        """
        for each ticker add ranking for each of the tags
        """
        for ticker_obj in self.tickers.values():


            ticker_obj_data = ticker_obj.get_analyzed_data()
            for source ,data in ticker_obj_data.items():

                if source not in self.industry_data[cfg.TICKERS]:
                    self.industry_data[cfg.TICKERS].update({source : {}})

            # add mktshare data
                try:
                    mktshare = float(data[cfg.MKTCAP]) / float(self.industry_data[cfg.MKTCAP_TOTAL])
                    # ticker_obj.add_data_to_analyzed_data(cfg.MKTSHARE, mktshare)

                    # add makret share data to self- intdustry data
                    try:
                        self.industry_data[cfg.TICKERS][source].update({cfg.MKTSHARE : mktshare})
                    except:
                        self.industry_data[cfg.TICKERS].update({source : {cfg.MKTSHARE : mktshare}})
                except:
                    pass

    def _add_ranking_data_to_tickers(self):
        df = pd.DataFrame.from_dict(dict(zip(self.tickers, [i.get_analyzed_data() for i in self.tickers.values()])),orient = 'index')

        # sort for each param and get the index of each ticker after sorting
        df_params = df.columns
        for param in df_params:
            temp_df = df.sort_index()
            temp_df = temp_df.sort_values(param, ascending = False)
            ratings = dict(zip(temp_df.index, [i for i in range(len(temp_df.index))]))
            for ticker, tick_rating in ratings.items():
                self.tickers[ticker].add_data_to_analyzed_data(param + "_Rating", tick_rating)

    def calc_ranking_data(self):
        for source, data in self.industry_data[cfg.TICKERS].items():
            df = pd.DataFrame.from_dict(dict(zip(self.tickers, [i.get_analyzed_data()[source] for i in self.tickers.values()])),orient = 'index')

            df_params = df.columns
            for param in df_params:
                temp_df = df.sort_index()
                temp_df = temp_df.sort_values(param, ascending = False)
                ratings = dict(zip(temp_df.index, [i for i in range(len(temp_df.index))]))
                for ticker, tick_rating in ratings.items():
                    print(ticker,tick_rating)
                    self.tickers[ticker].add_data_to_analyzed_data(source, param + "_Rating", tick_rating)

    def set_last_update(self):
        self.last_update = proj_utils.get_date()
