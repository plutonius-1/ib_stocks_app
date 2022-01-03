from cfg import *
from proj_utils import *


class localDataMngr_c:
    def __init__(self):
        pass



    #==============================================
    # Local Data Existance functions

    def raw_xml_data_exists(self, ticker, source):
        ticker = ticker.upper()
        postfix = "_"+FUND_REQ_TYPES_DICT["ReportsFinStatements"]
        search_path = None

        if source == IB:
            search_path = IB_DATA_PATH + ticker + "/" + ticker + postfix
        else:
            raise f"{__name__} : raw_xml_data_exists - not supporting lookup for source: {source} - need an update"

        return search_path

    def raw_processed_data_exists(self, ticker, source):
        ticker = ticker.upper()
        postfix = PROCESSED_FUNDAMENTAL_XML+".pkl"
        search_path = None

        if source == IB:
            search_path = IB_PROCESSED_PATH + ticker + "/" + ticker + postfix
        else:
            raise f"{__name__} : raw_xml_data_exists - not supporting lookup for source: {source} - need an update"

        return search_path

    #==============================================
    # object dates check
    def data_out_of_date(self, ticker, source):
        processed_raw_data_path = self.raw_processed_data_exists(ticker, source)

        if (processed_raw_data_path is None):
            return None

        # get the processed fund data as {"Q_data" : data, K_data : data}
        Q_K_dict = pd.read_pickle(processed_raw_data_path)
        Q_data   = Q_K_dict["Q_data"]
        K_data   = Q_K_dict["K_data"]


        return
