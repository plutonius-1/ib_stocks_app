import cfg
import proj_utils
import proj_ibtws_c
import threading
YES = "y"
NO  = "n"


class App_c:
    def __init__(self, **kwargs):
        self.verify_app_structure()

        # creates an IB TWS API and start a thread to run it
        self.ib_api = proj_ibtws_c.IbTws(host = kwargs[cfg.HOST],
                                    port = kwargs[cfg.PORT],
                                    clientId = kwargs[cfg.CLIENTID])
        self.ib_api_run_thread = threading.Thread(target = self.ib_api.run)
        self.ib_api_run_thread.start()

    def get_ticker_data(self, function, **kwargs):
        ticker = kwargs["ticker"]
        self.ib_api.call_function(cfg.GET_FUNDUMENTALS, ticker = ticker)

    def verify_app_structure(self):
        for _dir in cfg.BASIC_APP_STURCTURE_DIRS:
            proj_utils.check_dir_exists(_dir)

    def research_stock(self, ticker : str):
        """data we want:
        # 1) stock analysis from compDataAnalysis - this is the formal analysis of a company based on its fundamantals
        # 2) basic market research - provide a DF/excel compering the ticker were intersted in with its competitors
        # 3) comperative analysis - deep analysis of all the relevant competitors - based on similiar ratios like relevant makret cap etc...
        """
        # first check if relevant data exists
        # raw data
        raw = [proj_utils.check_file_exist(cfg.RAW_DATA_PATH + "/" + ticker + "/" + ticker + "_" +i) for i in cfg.FUND_REQ_TYPES_DICT.values()]
        raw = False in raw
        self.get_ticker_data(function = cfg.GET_FUNDUMENTALS, ticker = ticker)


    def research_stocks(self, tickers : list):
        for t in tickers:
            self.research_stock(t)


def main():
    host1 = "192.168.0.183"
    dunbros = "10.10.4.107"
    host3 = "10.1.10.150"

    app = App_c(host = host1, port = 7496, clientId = 10)
    reaserch = input("\nReasearch a stocks? (Y/N)\n").lower()
    while reaserch != YES and reaserch != NO:
        reaserch = input("\nReasearch a stocks? (Y/N)\n").lower()

    # get list of stocks
    if (reaserch == YES):
        stocks = input("provide tickers: (directly or provide path to text file containg them) ")
        stocks = stocks.split()
        stocks_ = []
        for s in stocks:
            if (".txt" not in s):
                stocks_.append(str(s).upper())
            else:
                assert cfg.os.path.exists(s)
                with open(s, "r") as f:
                    txt = f.read()
                txt = txt.split()
                stocks_ += [str(i).upper() for i in txt]

        app.research_stocks(stocks_)

    else:
        pass



if __name__ == "__main__":
    main()
