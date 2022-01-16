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
    def is_data_out_of_date(self, ticker, source):
        processed_raw_data_path = self.raw_processed_data_exists(ticker, source)

        if (processed_raw_data_path is None):
            return False

        # get the processed fund data as {"Q_data" : data, K_data : data}
        Q_K_dict = pd.read_pickle(processed_raw_data_path)
        _Q_data   = Q_K_dict[Q_data]
        _K_data   = Q_K_dict[K_data]

        q_dates = [norm_date(data['date']) for idx, data in _Q_data["INC"].items()]
        k_dates = [norm_date(data['date']) for idx, data in _K_data["INC"].items()]

        update = should_update_object(q_dates[0], get_date(), QUARTERLY_MIN_TIME_FOR_UPDATE) or \
                 should_update_object(k_dates[0], get_date(), YEARLY_MIN_TIME_FOR_UPDATE)
        return not update

    def add_raw_data_to_existing_processed_raw_data(self,
                                                 new_data : dict,
                                                 old_data  : dict):
        def shift_dict_keys(d : dict):
            shifted_d = {}
            for k,v in d.items():
                shifted_d.update({str(int(k) + 1) : v})
            return shifted_d

        def merge_old_and_new_fund_data(old_data, new_data):

            old_data_copy = old_data
            for new_type, new_statement_data in new_data.items():

                # get the old statement data
                old_statement_data = old_data[new_type]
                for new_index, new_date_data in new_statement_data.items():

                    new_date = new_date_data['date']
                    old_statement_dates = [norm_date(d['date']) for d in old_statement_data.values()]
                    if new_date not in old_statement_dates:
                        old_statement_data = shifted_d(old_statement_data)
                        old_statement_data.update({'0':new_date_data})
                old_data_copy[new_type] = old_statement_data
            return old_data_copy

        old_q_data = old_data[Q_data]
        old_k_data = old_data[K_data]
        new_q_data = new_data[Q_data]
        new_k_data = new_data[K_data]

        # Querterlies
        _Q_data = merge_old_and_new_fund_data(old_q_data, new_q_data)

        # Yearly
        _K_data = merge_old_and_new_fund_data(old_k_data, new_k_data)

        return {Q_data : _Q_data, K_data : _K_data}
