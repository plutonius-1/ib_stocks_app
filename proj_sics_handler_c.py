import cfg
import proj_utils
import IbSnapshotAnalyzer
import proj_snapshotXmlReader
import proj_finStatementsXmlReader


class Sics_handler_c:
    def __init__(self, ibtws_api):

        # tws running client
        self.tws_api = ibtws_api

        # import XML readers
        self.snapshotXmlReader = proj_snapshotXmlReader.snapshotXmlReader()
        self.finStatementXmlReader = proj_finStatementsXmlReader.finStatementXmlReader()

        # get the local copy of the sics dict
        self.sic_dict = self.get_local_sics_dict()

        # paths inits
        self.local_sic_code_path = cfg.SIC_CODES_PATH
        self.local_sic_dict_path = cfg.SIC_DICIONARY_PATH
        proj_utils.check_dir_exists(self.local_sic_code_path)
        proj_utils.check_dir_exists(self.local_sic_dict_path)


    #### GETS ####

    def get_comp_data(self):

        pass

    def get_local_sics_dict(self):
        if (not os.path.exists(cfg.SIC_DICIONARY_PATH)):
            new_dict = {}
            df = pd.DataFrame.from_dict(new_dict)
            df.to_pickle(cfg.SIC_DICIONARY_PATH)

        return pd.DataFrame.from_pickle(cfg.SIC_DICIONARY_PATH)

    #### SETS ####
    def update_sic_dict_comp_data(self,
                                  processed_fund_obj,
                                  processes_snapshot_obj,
                                  processes_finSummery):
        """
        go to local copy of sic_dict and update the companies datas
        reminder - compay data looks like:
        { "TICKER" :
            {
            "fundumentals" : fund_obj,
            "snapshot"     : snapshot_obj
            "finSummert"   : finSummert_obj
            }
        }
        """


        return

    ###
    def scrape_tickers_by_sic(self,
                              sic):
        """
        returns a list of all tickers for given SIC
        """

        # get all the tickers correlated with the given SIC that are active at 2021
        sic_tickers = IbSnapshotAnalyzer.get_companies_by_sic(str(sic))

        # for each of the ticker make a request from IB
        for ticker in sic_tickers:
            self.tws_api.call_function(cfg.GET_FUNDUMENTALS) #  saves 4 files to cfg.IB_FINANCIALS_PATH = ./ib_data/financials/"ticker"_fundReqType... (see IbTWS_c)
            # get different data objects from xml to build the main sics dic
            fundumentals = self.finStatementXmlReader.get_fundamentals_obj()

        return





