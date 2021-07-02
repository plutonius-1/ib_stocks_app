import cfg
YES = "y"
NO  = "n"


class App_c:
    def __init__(self):
        self.verify_app_structure()


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


    def research_stocks(self, tickers : list):
        for t in tickers:
            self.research_stock(ticker)


def main():
    app = App_c()
    reaserch = input("Reasearch a stocks? (Y/N)").tolower()
    while reaserch != YES and reaserch != NO:
        reaserch = input("Reasearch a stocks? (Y/N)").tolower()

    # get list of stocks
    if (reaserch == YES):
        stocks = input("provide tickers: (directly or provide path to text file containg them)")
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
        exit()




if __name__ == "__main__":
    main()
