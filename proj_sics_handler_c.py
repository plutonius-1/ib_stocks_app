import threading
import cfg
import proj_utils
import proj_sec_scraping_utils
import proj_snapshotXmlReader
import proj_finStatementsXmlReader
from proj_industry_c import Industry_c
from cfg import os
from cfg import pd
from cfg import pickle

### RATIOS CONTS ###
MKTCAP = cfg.MKTCAP
VOL10DAVG = cfg.VOL10DAVG
EV        = cfg.EV
# PER SHARE DATA #
TTMREVPS = cfg.TTMREVPS # rev per share
QBVPS = cfg.QBVPS # book val per share
QCSHPS = cfg.QCSHPS
TTMCFSHR = cfg.TTMCFSHR
TTMDIVSHR = cfg.TTMDIVSHR

# OTHER RATIOS #
TTMGROSMGN = cfg.TTMGROSMGN
TTMROEPCT  = cfg.TTMROEPCT
TTMPR2REV  = cfg.TTMPR2REV
PEEXCLXOR  = cfg.PEEXCLXOR
PRICE2BK   = cfg.PRICE2BK
COMPARISON_PARAMS = cfg.COMPARISON_PARAMS

## GENERAL CONSTS ##
ANALYZE = cfg.ANALYZE

class Sics_handler_c:
    def __init__(self, ibtws_api):

        # tws running client
        self.tws_api = ibtws_api

        # import XML readers
        self.snapshotXmlReader = proj_snapshotXmlReader.snapshotXmlReader_c()
        self.finStatementXmlReader = proj_finStatementsXmlReader.finStatementsXmlReader_c()

        # get the local copy of the sics dict
        # self.sic_dict = self.get_local_sics_dict()

        # paths inits
        self.local_sic_code_path = cfg.SIC_CODES_PATH
        self.local_sic_dict_path = cfg.SIC_DICIONARY_PATH
        # proj_utils.check_dir_exists(self.local_sic_code_path) # TODO -make func "check_file_exist"
        # proj_utils.check_dir_exists(self.local_sic_dict_path)


    #### GETS ####

    def get_comp_data(self):

        pass

    def get_local_sics_dict(self):
        if (not os.path.exists(cfg.SIC_DICIONARY_PATH) or
            os.path.getsize(cfg.SIC_DICIONARY_PATH) == 0):
            return {}
        else:
            with open(cfg.SIC_DICIONARY_PATH, "rb") as f:
                data = pickle.load(f)
            return data

    #### SETS ####

    ###
    def scrape_tickers_by_sic(self,
                              sic):
        """
        returns a list of all tickers for given SIC
        """

        # get all the tickers correlated with the given SIC that are active at 2021
        sic_tickers = proj_sec_scraping_utils.get_companies_by_sic(str(sic))

        return sic_tickers

    def scrape_ticker_ib_data(self, tickers : list):
        # for each of the ticker make a request from IB
        for ticker in tickers:
            self.tws_api.call_function(cfg.GET_FUNDUMENTALS, ticker = ticker) #  saves 4 files to cfg.IB_FINANCIALS_PATH = ./ib_data/financials/"ticker"_fundReqType... (see IbTWS_c)



    def update_local_sic_dict_by_sic(self, sic):

        sic = str(sic)

        local_dict_copy = self.get_local_sics_dict()

        # if (sic not in local_dict_copy):
            # local_dict_copy.update({sic:{}})

        # Get companies by tickers from SEC
        sic_tickers = self.scrape_tickers_by_sic(sic)

        # Get (download) all the data of the companies via IB
        self.scrape_ticker_ib_data(sic_tickers)

        proj_utils.print_sleep_msg(15, "wait response from IB to end") # TODO - implament a general indicator from IBAPI to signal all things return

        if (sic not in local_dict_copy):
            # make a new industry Obj
            industry = Industry_c(industry_name = None, SIC = sic)

        else:
            industry = local_dict_copy[sic]

        # update local sic dict
        for ticker in sic_tickers:
            fundumentals_obj = None
            snapshot_obj     = None
            # first update ticker data for XML readers
            try:
                self.finStatementXmlReader.set_ticker(ticker)
            except:
                pass
            try:
                self.snapshotXmlReader.set_ticker(ticker)
            except:
                pass

            # get different data objects from xml to build the main sics dic
            try:
                fundumentals_obj = self.finStatementXmlReader.get_fundamentals_obj()
            except:
                pass
            try:
                snapshot_obj     = self.snapshotXmlReader.get_snapshot_obj()
            except:
                pass

            ticker_data = {
                           cfg.FUNDAMENTALS : fundumentals_obj,
                           cfg.SNAPSHOT     : snapshot_obj
                          }
            # print("funds obj: {}\n snap: {}\n".format(fundumentals_obj, snapshot_obj))
            # update the local dict copy
            industry.add_ticker_data(ticker = ticker, ticker_data = ticker_data)

        local_dict_copy[sic] = industry
        self.save_sic_dictionary(local_dict_copy)


    def analyze_industry(self, sic):
        sic = str(sic)
        local_dict_copy = self.get_local_sics_dict()
        industry = local_dict_copy[sic]
        print("Industry pre-analyze: ", industry)
        industry.analyze_industry_after_tickers_are_added()
        print("Industry post-analyze: ", industry)
        local_dict_copy[sic] = industry
        self.save_sic_dictionary(local_dict_copy)

    def save_sic_dictionary(self, local_dict_copy):
        with open (cfg.SIC_DICIONARY_PATH, "wb") as f:
            pickle.dump(local_dict_copy, f, pickle.HIGHEST_PROTOCOL)
            f.close()


    def clear_existsing_dic(self):
        """
        Delets and replace with empty dic
        """
        ans = None
        while ans != "Y" and ans != "N":
            ans = input("Are you sure you want to delete the SICs dictionary? (Y/N)")
        if (ans == "Y"):
            os.remove(cfg.SIC_DICIONARY_PATH)
            self.save_sic_dictionary({})
        return

    def update_sic_codes_from_sec(self):
        """
        Updates the local dictionary of sic codes and thier name
        """
        import proj_marketReaseach
        mr = proj_marketReaseach.MarketReasercher()
        mr.update_sic_codes()
        return
#############################
import IbTWS_c

# host1 = "192.168.0.100"
# dunbros = "10.10.4.107"
# host3 = "10.1.10.150"

# ib_tws = IbTWS_c.IbTws(host = host1, port = 7496, clientId = 10)
# run_thread = threading.Thread(target = ib_tws.run)
# run_thread.start()

# proj_utils.print_sleep_msg(5)

# sic_handler = Sics_handler_c(ib_tws)

# sic_handler.clear_existsing_dic()
# proj_utils.print_sleep_msg(5)

# # sic_handler.update_local_sic_dict_by_sic(2100)
# # sic_handler.analyze_industry(2100)
# sics_df = pd.read_pickle(cfg.SIC_CODES_PATH) # all SICS from SEC
# for sic_code in sics_df["SIC Code"][:100]:
    # sic_code = str(sic_code)
    # sic_handler.update_local_sic_dict_by_sic(sic_code)
    # sic_handler.analyze_industry(str(sic_code))

# # proj_utils.print_sleep_msg(5)
# # sic_handler.analyze_sic_tickers(2100)

# ib_tws.disconnect()
