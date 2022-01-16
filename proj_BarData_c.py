from ibapi.common import BarData
import ibapi
from ibapi import utils
import cfg
from cfg import pickle
from cfg import pd
import proj_utils

class Bar_data_c(BarData):
    """
    extened class from IBAPI common class.
    Used as a generic base class for local classes
    """
    def __init__(self, ib_bar = None):
        BarData.__init__(self)
        if (ib_bar != None):
            self.date = ib_bar.date
            self.open = ib_bar.open
            self.high = ib_bar.high
            self.low  = ib_bar.low
            self.close = ib_bar.close
            self.volume = ib_bar.volume
            self.wap = ib_bar.wap
            self.barCount = ib_bar.barCount



    def get_close(self):
        return self.close
    def get_date(self):
        return self.date
    def get_open(self):
        return self.open
    def get_high(self):
        return self.high
    def get_low(self):
        return self.low
    def get_volume(self):
        return self.volume
    def get_wap(self):
        return self.wap
    def get_bar_count(self):
        return self.barCount

class Bars_data_c:
    """
    This class holds bars (plural) data.
    In addtion holds generic functions to manipuate and calculate
    different calcs on bars
    """
    def __init__(self):
        self._ticker = None
        self._type   = None
        self._bars   = []

    #================================
    ### Calculations functions ###
    #================================


    #================================
    ### Utils functions ###
    #================================
    def add_bar_data(self, bar_data):
        self._bars.append(bar_data)
        return None

    def save_bars_data(self):
        ticker = self._ticker
        assert ticker != None, f'{__name__}: self.ticker is None'
        path = cfg.IB_BAR_DATA_PATH + ticker + "/"
        proj_utils.check_dir_exists(path)
        name = ticker + cfg.BARS_DATA_POSTFIX
        tmp_obj = Bars_data_c()
        tmp_obj.set_type(self.get_type())
        tmp_obj.set_bars_data(self.get_bars_data())
        tmp_obj.set_ticker(self.get_ticker())
        with open(path + name + '.pkl', 'wb') as f:
            pickle.dump(tmp_obj, f, pickle.HIGHEST_PROTOCOL)
            print(f'{__name__}: saved {ticker} bars data')
        return None

    def load_bars_data(self, ticker):
        name = ticker.upper() + cfg.BARS_DATA_POSTFIX
        path = cfg.IB_BAR_DATA_PATH + ticker + "/"
        abs_path = path + name + ".pkl"
        if proj_utils.check_file_exist(abs_path):
            with open(abs_path, 'rb') as f:
                return pickle.load(f)
        print(f'{__name__}: did not find bars data for {ticker} at {abs_path}')
        return None

    #================================
    ### Set functions ###
    #================================
    def set_ticker(self, ticker):
        self._ticker = ticker.upper()
        return None

    def set_type(self, _type):
        self._type = _type
        return None

    def set_bars_data(self, bars : list):
        self._bars = bars
    #================================
    ### Get functions ###
    #================================
    def get_bars_data(self):
        return self._bars

    def get_ticker(self):
        return self._ticker

    def get_type(self):
        return self._type

    def _get_bars_by_name(self, col_name):
        funcs_dic = {
            'close' : Bar_data_c.get_close,
            'open'  : Bar_data_c.get_open,
            'high'  : Bar_data_c.get_high,
            'low'   : Bar_data_c.get_low,
            'volume': Bar_data_c.get_volume,
            'wap'   : Bar_data_c.get_wap,
            'date'  : Bar_data_c.get_date

        }
        f = funcs_dic[col_name]
        # res_dict = {col_name : {}}
        res_dict = {}
        for bar_obj in self._bars:
            date = proj_utils.norm_date(bar_obj.get_date())
            val  = f(bar_obj)
            # res_dict.update({str(date) : float(val)})
            res_dict.update({str(date) : {col_name:float(val), "date" : str(date)}})
        res = pd.DataFrame.from_dict(res_dict, orient = 'index')
        res.name = col_name
        return res

    def get_close_bars(self):
        return self._get_bars_by_name('close')
    def get_high_bars(self):
        return self._get_bars_by_name('high')
    def get_open_bars(self):
        return self._get_bars_by_name('open')
    def get_low_bars(self):
        return self._get_bars_by_name('low')
    def get_volume_bars(self):
        return self._get_bars_by_name('volume')
    def get_wap_bars(self):
        return self._get_bars_by_name('wap')

#===============================
# Base class extends for different types
#===============================
class Bars_trades_data_c(Bars_data_c):
    def __init__(self):
        Bars_data_c.__init__(self)
        self.set_type("TRADES")

class Bars_midpoints_data_c(Bars_data_c):
    def __init__(self):
        Bars_data_c.__init__(self)
        self.set_type("MIDPOINT")


#========================
bars_data_objects_by_type = {
    "TRADES" : Bars_trades_data_c(),
    "MIDPOINT" : Bars_midpoints_data_c()
    # TODO continue with other types
}
