from defs import *
import os, sys
import supplumentalData as sd
import pandas as pd


TICKERS_DIR_NAME = "Tickers"
FILENAME_PREFIXES = {
    "IB" : "_IB", # interactive brokers
    "MW" : "_MW"  # market watch
}

class OsManager:
    def __init__(self):
        self.platform = sys.platform
        self.pwd      = None
        self.tikcers_dir = "./" + TICKERS_DIR_NAME

        # make a tikcers dir if not exists
        self._set_tickers_dir()

    def _set_tickers_dir(self):
        if (self.platform == 'linux'):
            self.pwd = os.getcwd()
            if (TICKERS_DIR_NAME not in os.listdir()):
                os.mkdir("./" + TICKERS_DIR_NAME)

    def load_ticker_data(self,
                         ticker,
                         data_source : str,
                         data_type : str
                         ):

        tickerdir_path = "./" + TICKERS_DIR_NAME + "/" + ticker + "/"
        file_name = ticker +  FILENAME_PREFIXES[data_source]
        file_path = tickerdir_path + file_name + "." + data_type
        if (ticker not in os.listdir(self.tikcers_dir)):
            return None

        if ((file_name + "." + data_type) not in os.listdir(tickerdir_path)):
            return None

        if (data_type == "pkl"):
            return pd.read_pickle(file_path)

        if (data_type == "csv"):
            return pd.read_csv(file_path)

        return None


    def save_ticker_data(self,
                         ticker : str,
                         data_source : str, # ie - IB, MW ...
                         data : pd.DataFrame,
                         data_type : str):
        """
        @ ticker: - ticker name
        @ data_source - (str) represetnt where the data came from ie - IB = interactive brokers, MW = marketwatch ...
        @ data - the data it self
        @ data_type : (str) - the postfix of the file - pkl, csv ...

        """

        # if no dir for ticker create
        tickerdir_path = "./" + TICKERS_DIR_NAME + "/" + ticker
        file_name = ticker +  FILENAME_PREFIXES[data_source]
        df = data
        if (ticker not in os.listdir(os.getcwd() + "/" + TICKERS_DIR_NAME)):
            os.mkdir(tickerdir_path)

        file_path = tickerdir_path + "/" + file_name + "." + data_type
        if (data_type == "pkl"):
            data.to_pickle(file_path)

        elif (data_type == "csv"):
            data.to_csv(file_path)

        print("saved {}.{} at: {}".format(file_name, data_type, tickerdir_path))


    def get_supplumental_data(self,
                              ticker : str,
                              data_source : str,
                              data_type : str):
        """
        returns DF
        """
        # TODO add function - in case local supllumental data exists download new data and append to old

        local_data =  self.load_ticker_data(ticker = ticker,
                                 data_source = data_source,
                                 data_type = data_type)
        print("local data = ", local_data)
        if (local_data == None):
            print("Downloading {} supplumental data".format(ticker))
            data = sd.get_data(ticker)
            data = pd.DataFrame.from_dict(data)
            self.save_ticker_data(ticker, data_source, data, data_type)
        else:
            data = local_data

        return data
