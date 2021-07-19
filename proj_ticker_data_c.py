import cfg
import proj_utils
from proj_utils import bcolors

class Ticker_data_c:
    def __init__(self):
        self._ticker          = None
        self._raw_data        = {}
        self._analyzed_data   = {}
        self._in_industry_avg = {}
        self._last_update     = cfg.DEFAULT_OBJECT_LAST_UPDATE

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
        return analyzed_data

    def calc_change_over_period(self, series : cfg.pd.Series):
        # first assert that index (dates)is increasing
        # ie:
        # 2015 data
        # 2016 data
        # ...  data
        ser = series.sort_index()

        ser = ser.pct_change()
        ALSO FIX in industry class
        return ser
    #### SETS ####
    def set_last_update(self):
        pass

    def set_ticker(self, ticker):
        self._ticker = ticker

    def set_raw_data(self, raw_data):
        self._raw_data = raw_data
        self._analyzed_data = self._analyze_data(self._raw_data)

    def set_in_indutry_avg(self, data_name : str ,status : bool):
        self._in_industry_avg.update({data_name : status})

    def add_data_to_analyzed_data(self, tag, val):
        self._analyzed_data.update({tag : val})

    def set_last_update(self):
        self._last_update = proj_utils.get_date()

    #### GETS ####
    def get_ticker(self):
        return self._ticker

    def get_raw_data(self):
        return self._raw_data
    def get_analyzed_data(self):
        return self._analyzed_data
    def get_in_industry_avg(self):
        return self._in_industry_avg
    def get_last_update(self):
        return self.last_update

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

