import xml.etree.ElementTree as ET
import pandas as pd
import pickle
import cfg

class financialSummeryXmlReader_c:
    def __init__(self):
        self.ticker = None
        self.financial_summery_path = None
        self.TOTAL_REVENUE_INFO_DIR_PATH = "./TotalRevenues"
        self.EPS_INFO_DIR_PATH           = "./EPSs"

    def get_revenues(self):
        assert self.ticker != None
        revenues = proj_utils.get_xml_elem(self.financial_summery_path,
                                           self.TOTAL_REVENUE_INFO_DIR_PATH)
        return

    def get_epss(self):

        return

    def set_ticker(self, ticker):
        self.ticker = ticker
        self.financial_summery_path = cfg.IB_FINANCIALS_PATH + self.ticker + "_financial_summary.xml"
