import cfg
import proj_utils
from base_data_obj_c import Base_data_obj_c as base_data_c
from proj_utils import bcolors

DATA_SOURCES = {"IB":"IB"}


class Ticker_data_c:
    def __init__(self):
        self._ticker = None
        self._raw_data = {} # tags are sources - IB, etc...
        self._raw_statements = {}
        self._pct_change_period_data = {}
        self._analyzed_data = {}

    #### sets ####
    def set_raw_data(self, data, source):
        assert source in DATA_SOURCES
        self._raw_data.update({source : data})

    def set_ticker(self, ticker):
        self._ticker = ticker.upper()

    def set_raw_statements(self):
        """
        from raw data set the raw statements
        """

        def add_data_obj(data_obj, source):
            try:
                self._raw_statements[source].update({data_obj.get_name() : data_obj})
            except:
                self._raw_statements.update({source : {data_obj.get_name(): data_obj}})

        def set_raw_statement_by_source(source, raw_data):
            if source == DATA_SOURCES["IB"]:
                fundametals_Q = raw_data["fundamentals"]["Q_data"]
                fundametals_K = raw_data["fundamentals"]["K_data"]
                for statement in fundametals_Q:
                    data_obj = base_data_c()
                    data_obj.set_name(statement)
                    data_obj.set_data(fundametals_Q[statement])
                    data_obj.set_frequancy(cfg.Q)
                    add_data_obj(data_obj, source)

                for statement in fundametals_K:
                    data_obj = base_data_c()
                    data_obj.set_name(statement)
                    data_obj.set_data(fundametals_K[statement])
                    data_obj.set_frequancy(cfg.K)
                    add_data_obj(data_obj, source)
            return None

        # iterate over all sources and add relevant data to ticker obj
        for source, raw_data in self._raw_data.items():
            set_raw_statement_by_source(source, raw_data)

    def set_pct_change_data(self):
        for source, statements in self._raw_statements.items(): # source : {name : data_obj}
            for name, s in statements.items(): # {name : data_obj}
                df = s.get_data()
                df_name = s.get_name()
                df_freq = s.get_frequancy()

                # make sure we get DF from raw statement
                if (type(df) == dict):
                    df = cfg.pd.DataFrame.from_dict(df)

                # create the new pct df
                pct_df = cfg.pd.DataFrame()

                # iterate over each line in statement and calc the pct change
                for tag in df.index:
                    pct_df = pct_df.append(self._calc_change_over_period(df.loc[tag]))
                    data_obj = base_data_c()
                    data_obj.set_name(df_name)
                    data_obj.set_frequancy(df_freq)
                    data_obj.set_data(pct_df)

                self._pct_change_period_data.update({source : {df_name : data_obj}})

        return None

    def add_data_to_analyzed_data(self, source, tag, val):
        if (source in self._analyzed_data):
            self._analyzed_data[source].update({tag : val})
        else:
            self._analyzed_data.update({source :{tag : val}})
        return None

    def make_analyzed_data(self):
        for source in self._raw_data.keys():

            # get the relevant comperison parameters in accorance to the source
            comper_params = cfg.SOURCES_COMPER_PARAMS[source]

            for tag in comper_params:
                try:
                    val = proj_utils._finditem(self._raw_data[source], tag)
                    if (val == None):
                        print(bcolors.WARNING + "Did not find {} in data - addding None".format(tag) + bcolors.ENDC)
                    self.add_data_to_analyzed_data(source, tag, val)
                except:
                    pass
        return None

    def get_analyzed_data(self):
        return self._analyzed_data

    ## Utils ##
    def _calc_change_over_period(self, series : cfg.pd.Series):
        ser = series.sort_index()
        ser_shifted = ser.shift(1)
        diff = ser - ser_shifted
        pct_change = diff / abs(ser_shifted)
        return pct_change


