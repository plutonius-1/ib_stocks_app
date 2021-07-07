# TODO remove imports after including

from osManager import OsManager as Om
import re
import requests
import pandas as pd
import osManager

## URL RELATED ##
START_PAGE      = 0
INDUSTRIES_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC={}&owner=exclude&match=&start={}&count=100&hidefilings=0"
COMP_FILINGS_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&owner=include&count=100&hidefilings=0"
CIK_URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
SIC_CODES_URL = "https://www.sec.gov/info/edgar/siccodes.htm"
#################

### OS RELATED ###
SIC_CODES_PATH = "./SICS/sic_codes.pkl"
SIC_DICIONARY_PATH = "./SICS/dictionary.pkl"



class MarketReasercher:
    def __init__(self, **kwargs):

        # initilize os manager
        self.om = Om()

        # get the local copy of SICs df
        self.sic_codes_df = self._get_sic_codes_df()

        # update if needed
        self.sic_codes_updated = False
        # self.update_sic_codes()

    def get_company_cik(self, ticker : str):
        CIK_RE = re.compile(r'.*CIK=(\d{10}).*')
        results = CIK_RE.findall(requests.get(CIK_URL.format(ticker)).content)
        assert(len(results) > 0 ), "MarketReasercher - Did not find the CIK for {}".format(ticker)
        return str(results[0])

    def get_company_sic(self, ticker : str):
        """
        @ param ticker - the ticker of the comapny we want to find the SIC for
        returns the sic as int
        """
        SIC_RE = re.compile(r'.*SIC: \d+')
        CIK    = self.get_company_cik(ticker)
        results = SIC_RE.findall(requests.get(COMP_FILINGS_URL.format(CIK)).content)
        assert len(results) >0, "MarketReasercher - Did not find the SIC for {}".format(ticker)
        SIC = results[0].split()[1]
        return SIC

    ### LOCAL SIC CODES MANAGEMENT ###
    def _get_sic_codes_df(self):
        try:
            sic_dic = pd.read_pickle(SIC_CODES_PATH)
        except:
            sic_dic = pd.DataFrame()
        return sic_dic

    def update_sic_codes(self):

        resp = self.assert_table_in_response(SIC_CODES_URL)
        assert resp != None, "No tables in SIC CODES URL: {}".format(SIC_CODES_URL)

        df = pd.read_html(resp.content) # should return a list of tables
        df_list =[]
        for i in df:
            if i.columns.dtype == "int64":
                new_header = i.iloc[0]
                i = i[1:]
                i.columns = new_header
                df_list.append(i)
        # filter all the DFs that do not include the SIC in thier columns names
        sic_table = list(filter(lambda x : "SIC" in "".join([str(i) for i in x.columns]), df_list))
        assert (len(sic_table) == 1), "got more than 1 table from {}".format(SIC_CODES_URL)

        sic_table = sic_table[0]

        sic_table.to_pickle(SIC_CODES_PATH)
        # if sic_table != self.sic_codes_df:
            # sic_table.to_pickle(SIC_CODES_PATH)
            # self.sic_codes_updated = True
            # return
        return


    def update_sic_dictionary(self):
        sic_dic = self.get_sic_dictionary()
        sics_codes = self.sic_codes_df["SIC code"]

        if sic_dic.empty():
            for code in sics_codes:

                # initilize dict for {SIC:{company : company info}}
                SIC_DICT = {str(code) : {}}

                start = 0
                resp = self.assert_table_in_response(INDUSTRIES_URL.format(str(code), str(start)))
                while resp != None:
                    companies_table = pd.read_html(resp.content)[0]
                    start += 100
                   # sdk;lakd;lask;l  ## TODO - since Market watch dont have all acompanies - look to get all companies data via IB or Morning star
                                    ## TODO - also, use marketwatch all for comapnies we see on
                    resp = self.assert_table_in_response(INDUSTRIES_URL.format(str(code), str(start)))


        return

    def update_sic_companies_data(self):

        return

    def get_company_competitors_third_party(self, ticker):
        # TODO: get from MW list of competitors (?)
        return

    def get_company_sec_total_industry(self, ticker):
        # TODO: get the total industry based on SEC SIC codes from local file

        #

        return
    """
    usage flow:
        1) call method with a ticker param
        2) get in return the market share of ticker in according to a) 3rd part + b) SEC SIC

    Implementation:
        A) SEC
            a) hold a local dic: {"SIC code" : {all relevant companies and their valuation as Company objects}} * NOTE - THIS MEANS THAT THIS DICIONARY NEED TO BE UPDATED ONCE A WEEK OR SO
            b) when given the ticker, find its SIC according to SEC, then go to local dic, and find the relative market share.
            dic data organiztion:
            {
                "123" :
                {
                    "ticker1" : comp obj,
                    "ticker2" : comp obj
                }
            }

        B) Third party (MW?)
            a) go to the ticker 3rd party website and see who they say are the competitors
                *) check if IP API provides option like that
            b) get data (market cap etc...) for all of the above mentioned competitors, and return market share and industry trends

        GENERAL)
            a) also return the change in market (grow/decline) and maybe more stuff about the market in general
            b) like volatility
            c) compare to S&P and other index
            d) is the industry reletavly big? small? stable? position for growth?

    """

    def get_sic_dictionary(self):
        try:
            df = pd.read_pickle(SIC_DICIONARY_PATH)
        except:
            df = pd.DataFrame()

        return df
    ##################################


    ### GENERAL UTILS ###
    def assert_table_in_response(self, url):
        resp = requests.get(url)
        table_re = re.compile(r'table')

        assert resp.ok, "response NOT OK for : {}".format(url)
        if (len(table_re.findall("table")) > 0):
            return resp
        else:
            return None
    #####################


#####################################################

## Class (SicCompany) object
class SicCompany:
    THIRD_PARTYS_FINANCIALS_LINKS = {
        "MS" : "https://www.morningstar.com/stocks/xnys/{}/financials",
        "MW" : "https://www.marketwatch.com/investing/stock/{}/company-profile?mod=mw_quote_tab"
    }
    VALID_THIRD_PARTIES = ["MW"]

    def __init__(self):
        self.ticker = None
        self.last_date_update = None
        self.profiles = {}
        """
        Note ratios should be ???
        """

    ### SCRAPE ###
    def scrape_third_party_data(self):

        ### THIRD PARTY FILTER FUNCTIONS ###
        def mw_filter(df):
            if (df.empty == False):
                tags = "".join(str(df[df.columns[0]]))
                if ("Ratio" in tags or
                    "Turnover" in tags or
                    "Assets" in tags or
                        "Margin" in tags):
                    return True
                else:
                    return False
            return False

        filter_functions = {"MW":mw_filter}

        def get_and_varify_page(self,
                                third_party_name : str,
                                ticker : str):

            req = requests.get(self.THIRD_PARTYS_FINANCIALS_LINKS[third_party_name].format(ticker))
            if not req.ok or "table" not in req.text:
                return None
            else:
                filter_func = filter_functions[third_party_name]
                filterd_results = list(filter(filter_func, pd.read_html(req.content)))
                if (len(filterd_results) == 0):
                    return None
                merged_df = pd.concat(filterd_results)
            return merged_df

        for third_party_name in self.VALID_THIRD_PARTIES:
            profile_df = get_and_varify_page(self, third_party_name, self.ticker)
            self.profiles.update({third_party_name : profile_df})
        return


    ### SETS ###
    def set_ticker(self, ticker : str):
        self.ticker = ticker

    def set_last_date_update(self, date : str):
        self.last_date_update = None

    ### GETS ###
    def get_ticker(self):
        return self.ticker

    def get_last_date_update(self):
        return self.last_date_update

    def get_profiles(self):
        return self.profiles

    ### UTILS ###
# mr = MarketReasercher()
