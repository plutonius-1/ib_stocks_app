import cfg
import proj_utils
from proj_utils import bcolors

## CONSTS ##
PCT_CHANGE_POSTFIX = " pct change"


############

class Ticker_data_c:
    def __init__(self):
        self._ticker          = None
        self._raw_data        = {}
        self._analyzed_data   = {}
        self._raw_statements_dfs  = {}
        self._pct_change_statements_dfs = {}
        self._in_industry_avg = {}
        self._last_update     = cfg.DEFAULT_OBJECT_LAST_UPDATE
        self._k_tags_compare_to_industry = {}
        self._q_tags_compare_to_industry = {}

    def _analyze_data(self, raw_data):
        analyzed_data = {}
        for tag in cfg.COMPARISON_PARAMS:
            try:
                val = proj_utils._finditem(raw_data, tag)
                if (val == None):
                    print(bcolors.WARNING + "Did not find {} in data - addding None".format(tag) + bcolors.ENDC)
                analyzed_data.update({tag : val})
            except:
                pass

        # add statements dfs
        fundametals_Q = raw_data["fundamentals"]["Q_data"]
        fundametals_K = raw_data["fundamentals"]["K_data"]
        for statement in fundametals_Q:
            self.add_statement_df(statement + "_Q", fundametals_Q[statement])
        for statement in fundametals_K:
            self.add_statement_df(statement + "_K", fundametals_K[statement])

        # clac the pct change for all statements
        for statement_df in self._raw_statements_dfs:
            df = self._raw_statements_dfs[statement_df]
            pct_df = cfg.pd.DataFrame()
            for tag in df.index:
                pct_df = pct_df.append(self.calc_change_over_period(df.loc[tag]))
            self._pct_change_statements_dfs.update({statement_df : pct_df})

        return analyzed_data

    def calc_change_over_period(self, series : cfg.pd.Series):
        # first assert that index (dates)is increasing
        # ie:
        # 2015 data
        # 2016 data
        # ...  data
        ser = series.sort_index()
        ser_shifted = ser.shift(1)
        diff = ser - ser_shifted
        pct_change = diff / abs(ser_shifted)
        # pct_change.name = pct_change.name + PCT_CHANGE_POSTFIX
        return pct_change

    def add_statement_df(self, name : str, raw_statement : dict):
        self._raw_statements_dfs.update({name:cfg.pd.DataFrame.from_dict(raw_statement)})

    #### SETS ####
    def set_ticker(self, ticker):
        self._ticker = ticker

    def set_raw_data(self, raw_data):
        self._raw_data = raw_data
        self._analyzed_data = self._analyze_data(self._raw_data)

    def set_in_indutry_avg(self, data_name : str ,status : bool):
        self._in_industry_avg.update({data_name : status})

    def add_data_to_analyzed_data(self, tag, val):
        self._analyzed_data.update({tag : val})

    def update_k_tags_compare_to_industry(self, data : dict):
        dict_keys = [n.split("_")[0] for n in data.keys()]
        for name in cfg.STATEMENTS_NAMES:
            assert name in dict_keys, print(f'NAME : {name}, dict keys: {dict_keys}')
            self._k_tags_compare_to_industry.update({name : data[name+"_K"]}) # TODO

    def update_q_tags_compare_to_industry(self, data : dict):
        dict_keys = [n.split("_")[0] for n in data.keys()]
        for name in cfg.STATEMENTS_NAMES:
            assert name in dict_keys
            self._q_tags_compare_to_industry.update({name : data[name+"_Q"]}) # TODO

    def set_last_update(self):
        self._last_update = proj_utils.get_date()

    #### GETS ####
    def get_ticker(self):
        return self._ticker
    def get_raw_data(self):
        return self._raw_data
    def get_raw_statements_dfs(self):
        return self._raw_statements_dfs
    def get_analyzed_data(self):
        return self._analyzed_data
    def get_in_industry_avg(self):
        return self._in_industry_avg
    def get_last_update(self):
        return self.last_update
    def get_statements_df(self):
        return self._raw_statements_dfs
    def get_pct_change_statements_dfs(self):
        return self._pct_change_statements_dfs
    def get_line_from_statement(self, df : cfg.pd.DataFrame, tag : str):
        return df.loc[tag]
    def get_q_tags_compare_to_industry(self):
        return self._q_tags_compare_to_industry
    def get_k_tags_compare_to_industry(self):
        return self._k_tags_compare_to_industry

    def get_change_of_tag(self,
                          tag            : str,
                          Q_or_K         : str
                          ):
        """
        returns tuple of (last year/qurater value, change over last qurters/yealy on average)
        """
        res = self.find_line_in_pct_statements(tag, Q_or_K)
        if not res.dropna().empty:
            res = res.dropna()
            length = len(res)
            return (res[-1], res.cumsum()[-1] / length)
        return None, None


    def find_line_in_statements(self,tag : str, Q_or_K : str):
        res = None
        assert Q_or_K == "Q" or Q_or_K == "K"
        for s in self._raw_statements_dfs:
            if Q_or_K in s:
                statement = self._raw_statements_dfs[s]
                try:
                    res = self.get_line_from_statement(statement, tag)
                    return res
                except:
                    pass
        return res

    def find_line_in_pct_statements(self, tag : str, Q_or_K : str):
        res = cfg.pd.Series()
        assert Q_or_K == "Q" or Q_or_K == "K"
        for s in self._pct_change_statements_dfs:
            if Q_or_K in s:
                statement = self._pct_change_statements_dfs[s]
                try:
                    res = self.get_line_from_statement(statement, tag)
                    return res
                except:
                    pass
        return res


    ## OVERRIDES ##
    def analyze_data(self):
        self._analyze_data(self._raw_data)

    def __repr__(self):
        return("ticker: {} \nanalyzed_data: {}\nin industy avg: {}\n".format(
                self._ticker,
                self._analyzed_data,
                self._in_industry_avg ))

    def __eq__(self, other):
        if (self._ticker != other.ticker or
            self._raw_data != other.raw_data or
            self._analyzed_data != other.analyzed_data):
            return False
        return True

