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
        self.sources        = []
        self.industry_data  = {cfg.TICKERS : {},
                               cfg.MKTCAP_TOTAL : 0}    # initilize with empty tickers_dic -holds each tickers ranks and other comperative data
        self.industry_avg_data = {}
        self.industry_pct_change_data = {"IB":{}}
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

        # calc the WEIGHTED avarge pct change for each of the statemnts
        # Note - each statement is multiplied by the relative market share of each ticker
        self._calc_ind_pct_avg_change()


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

        # calc sum(w_i * x_i) - no need to devide by sum(w_i) since it is normilsed already
        norm_avg = 0.0

        for ticker in self.tickers:
            ticker_analyzed_data = ticker.get_analyzed_data()
            ticker_pct_data      = ticker.get_pct_change_period_data() # {source : {inc : data_obj, bal : data_obj, cas : data_obj}}

            # weight_i is the pct of the market share of each ticker
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
                    ticker_obj.add_data_to_analyzed_data(source, cfg.MKTSHARE, mktshare)

                    # add makret share data to self- intdustry data
                    try:
                        self.industry_data[cfg.TICKERS][source][ticker_obj.get_ticker()].update({cfg.MKTSHARE : mktshare})
                    except:
                        self.industry_data[cfg.TICKERS].update({source : {ticker_obj.get_ticker() : {cfg.MKTSHARE : mktshare}}})
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
                tag = param + "_Rating"
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
                    tag = param + "_Rating"
                    self.tickers[ticker].add_data_to_analyzed_data(source, tag, tick_rating)
                    try:
                        self.industry_data[cfg.TICKERS][source][ticker].update({tag : tick_rating})
                    except:
                        self.industry_data[cfg.TICKERS][source].update({ticker : {tag : tick_rating}})

    def _calc_ind_pct_avg_change(self):

        def _add_line_to_ind_pct_change(main_df : pd.DataFrame,
                                        line    : pd.Series):
            temp_df = main_df
            if (line.name) in temp_df.index:
                temp_df.loc[line.name] += line
                return temp_df
            else:
                return temp_df.append(line)

        def _get_original_df(self, data_obj : Base_data_obj_c, source : str):
            if not (data_obj.get_name() in self.industry_pct_change_data[source]):
                new_data_obj = Base_data_obj_c()
                new_data_obj.set_name(data_obj.get_name())
                new_data_obj.set_frequancy(data_obj.get_frequancy())
                new_data_obj.set_data(pd.DataFrame())
                try:
                    self.industry_pct_change_data[source].update({new_data_obj.get_name() : new_data_obj})
                except:
                    self.industry_pct_change_data.update({source : {new_data_obj.get_name() : new_data_obj}})

            return self.industry_pct_change_data[source][data_obj.get_name()]

        def _put_original_data(self, data_obj : Base_data_obj_c, source : str):
            self.industry_pct_change_data[source][data_obj.get_name()] = data_obj


        for ticker in self.tickers:

            # get the ticker precent change data
            pct_data = self.tickers[ticker].get_pct_change_period_data()

            for source, statements in pct_data.items():
                for data_type, data_obj in statements.items():

                    # get the original df
                    original_data_obj = _get_original_df(self, data_obj, source)
                    original_df = original_data_obj.get_data()

                    # get weight and multply each df
                    ticker_weight = self.tickers[ticker].get_analyzed_data()[source][cfg.MKTSHARE]

                    df = data_obj.get_data()

                    # augment the df to be normialsed by weight
                    df = df*ticker_weight

                    freq = data_obj.get_frequancy()
                    for line in df.index:
                        temp_line = df.loc[line]
                        original_df = _add_line_to_ind_pct_change(original_df, temp_line)
                    original_data_obj.set_data(original_df)
                    _put_original_data(self, original_data_obj, source)
        return


    def get_ticker_relatives(self,
                             ticker : str):
        try:
            ticker_data = self.tickers[ticker].get_pct_change_period_data() # returns {source : {data ...}}

            # per source
            for source, statements in ticker_data.items():
                # iterate over all pct change statements and compare to inudstry avg
                for statement_name ,statement_obj in statements.items():
                    tick_df = statement_obj.get_data()
                    inda_df = self.get_industry_pct_change_data()[source][statement_name]



        except:
            print(f"ticker :{ticker} not in industry")
            return None

    def set_last_update(self):
        self.last_update = proj_utils.get_date()

    def get_industry_pct_change_data(self):
        return self.industry_pct_change_data

    def add_source(self, src : str):
        if src not in self.sources:
            self.sources.append(src.upper())

    def get_sources(self):
        return self.sources

