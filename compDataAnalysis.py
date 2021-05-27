# -*- coding: utf-8 -*-

"""
Created on Sun Mar 14 14:09:08 2021

@author: avsha
"""

import xml.etree.ElementTree as ET
import pandas as pd
import pickle

from osManager import OsManager as om
from defs import *
from supplumentalData import *


R_D = 6.5 # TODO
ASSET_LIFE = 20
BUISNESS_TAX_RATE = 0.21

################
#### ASSETS ####

financial_assets_tags  = ["cash & equivalents",
                          "short term investments",
                          "cash and short term investments"]

opreational_assets_tags = ["accounts receivable - trade, net",
                          "total receivables, net",
                          "total inventory",
                          "prepaid expenses",
                          "other current assets, total",
                          "total current assets",
                          "property/plant/equipment, total - gross",
                          "accumulated depreciation, total",
                          "property/plant/equipment, total - net",
                          "goodwill, net",
                          "intangibles, net",
                          "other long term assets, total",
                          "total assets"
                          ]

extra_assets_tags       = []


#####################
#### LIABILITIES ####

financial_liab_tags = ["notes payable/short term debt",
                       "long term debt",
                       "total long term debt",
                       "total debt",
                       #"minority interest",
                       ]

opreational_liab_tags = ["accounts payable",
                           "accrued expenses",
                           "current port. of  lt debt/capital leases",
                           "other current liabilities, total",
                           "total current liabilities",
                           "other liabilities, total",
                           "total liabilities"]

################
#### EQUITY ####


equity_tags = ["common stock, total",
               "additional paid-in capital",
               "retained earnings (accumulated deficit)",
               "treasury stock - common",
               "other equity, total",
               "total equity",
               "total liabilities & shareholders' equity",
               "total common shares outstanding",
               "tangible book value per share, common eq"]

comp_analysis_template = {
    "bv_working_capital":None,
    "working_capital":None,
    "current_r&d_asset":None,
    "property/plant/equipment":None,
    "bv_invested_capital":None,
    "invested_capital":None,
    "adj_goodwill_intangibles":None,
    "adj_equity":None,
    "financial_leaverage":None,
    "ebit":None,
    "operating_margin":None,
    "bv_capital_turnover":None,
    "capital_turnover":None,
    "bv_roc":None,
    "roc":None,
    "roe":None,
    "non_cash_roe":None,
    "roa":None
    }

class CompDataAnalysis:

    def __init__(self, ticker):
        self.om = om()
        try:
            self.supplumental_data = self.om.get_supplumental_data(ticker = ticker,
                                                              data_source = "MW",
                                                              data_type = "pkl")
        except:
            pass

        self.master_data = None
        self.master_K_data = None
        self.master_Q_data = None


        # main statements
        self.BAL = None
        self.CAS = None
        self.INC = None

        self.BAL_K = None
        self.CAS_K = None
        self.INC_K = None

        # others
        self.Q_analysis = comp_analysis_template
        self.K_analysis = comp_analysis_template


    #### Helpers Functions ####
    def set_master_data(self, path_to_dic : str):
        """
        sets the data and the balance, cash, income acording to path_to_dic.
        dic paramter should be parsed raw data of a company give via IBAPI
        in the shape:
            {INC : {dates:{data}}, BAL : {dates:{data}}, ...}

        Parameters
        ----------
        path_to_dic : str
            DESCRIPTION.

        Returns
        -------
        None.

        """
        with open(path_to_dic, 'rb') as f:
            self.master_data = pickle.load(f)
        self.master_Q_data = self.master_data["Q_data"]
        self.master_K_data = self.master_data["K_data"]

        self.BAL = self.master_Q_data["BAL"]
        self.CAS = self.master_Q_data["CAS"]
        self.INC = self.master_Q_data["INC"]

        self.BAL_K = self.master_K_data["BAL"]
        self.CAS_K = self.master_K_data["CAS"]
        self.INC_K = self.master_K_data["INC"]
        return


    def sum_vectors_by_name(self,
                            statement : dict,
                            tags : list):
        res = pd.DataFrame()
        statement = pd.DataFrame.from_dict(statement)

        for tag in tags:
            if (res.empty):
                res = statement.loc[tag]
            else:
                res += statement.loc[tag]

        return res




    #### Calculations Functions ####

    def calc_working_capital(self,
                             balance_sheet : dict):
        assert balance_sheet != None ,"balance sheet is None"

        bal_df = pd.DataFrame.from_dict(balance_sheet)
        return self.sum_vectors_by_name(balance_sheet, ["total receivables, net",
                          "total inventory",
                          "prepaid expenses",
                          "other current assets, total"]) - self.sum_vectors_by_name(balance_sheet, ["accounts payable",
                           "accrued expenses",
                           "other current liabilities, total"])


    def calc_bv_working_capital(self,
                                balance_sheet : dict):
        assert balance_sheet != None ,"balance sheet is None"

        bal_df = pd.DataFrame.from_dict(balance_sheet)
        return bal_df.loc["total current assets"] - bal_df.loc["total current liabilities"]


    def calc_property_plant_equipment(self,
                                      balance_sheet : dict):
        bal_df = pd.DataFrame.from_dict(balance_sheet)

        return bal_df.loc["property/plant/equipment, total - net"]


    def calc_goodwill_intangibles(self,
                                  balance_sheet : dict):

        return self.sum_vectors_by_name(balance_sheet, ["goodwill, net",
                                                   "intangibles, net"]) / 2


    def calc_depriciated_rnd(self,
                             income_statement : dict):

        inc_df = pd.DataFrame.from_dict(income_statement)
        rnd_spending = inc_df.loc["research & development"]

        # reverse series
        rnd_spending = rnd_spending[::-1]

        ser = rnd_spending

        dic = {}

        div = len(ser)

        for idx in range(len(ser)):
            current_rnd_asset = 0.0
            for i in range(idx + 1):
                div = idx + 1
                current_rnd_asset += ser[i] * (i+1)/div
            dic.update({ser.index[idx]:current_rnd_asset})

        res = pd.Series(dic)
        res = res[::-1]

        return res
        # return current_rnd_asset


    def calc_invested_capital(self, analysis_group : dict , method = "direct"):
        """
        """
        if method == "direct":
            invested_capital    = analysis_group["working_capital"] + analysis_group["property/plant/equipment"]
            bv_invested_capital = analysis_group["bv_working_capital"] + analysis_group["property/plant/equipment"]
            return bv_invested_capital, invested_capital
        else:
            pass # TODO
            return None, None


    def calc_adjusted_equity(self,
                             analysis_group : dict,
                             balance_sheet : dict):
        """
        2 different adjustents needs to be done:
            A. if (tax assets > tax liablity) we subtruct the net from equity
            B. since we adjust the intangible and goodwill assets we subtruct
            the difference from equtity

        Returns
        -------
        None.

        """
        bal_df = pd.DataFrame.from_dict(balance_sheet)

        base_equity = bal_df.loc["total equity"]

        # A tax adjustemnt #
        # TODO - currently no tax assets/liab info from IB API
        tax_diff = 0 # TODO

        # B. goodwill & intengibles #
        bv_intangibles_goodwill = self.sum_vectors_by_name(balance_sheet,
                                                           ["goodwill, net",
                                                            "intangibles, net"])
        adj_intangibles_goodwill = analysis_group["adj_goodwill_intangibles"]

        goodwill_diff = abs(bv_intangibles_goodwill - adj_intangibles_goodwill)

        # adjust equity
        adj_equity = base_equity - (goodwill_diff + tax_diff)

        return adj_equity


    ### Basic Ratios ###

    def calc_financial_leverage(self,
                                analysis_group : dict,
                                balance_sheet : dict,
                                yearly_income_statement : dict):

        def calc_adjusted_assets(yearly_income_statement : dict,
                                 analysis_group : dict):
            """
            add:
                1) lease assets
                2) R&D assets
            Returns
            -------
            None.

            """
            df = pd.DataFrame.from_dict(yearly_income_statement)
            lease_liab = df.loc["capital lease obligations"]
            lease_assets = lease_liab / (R_D + (1/ASSET_LIFE))
            rnd_assets = analysis_group["current_r&d_asset"]

            res = lease_assets + rnd_assets
            return res


        ### accountent method ###
        t1 = self.sum_vectors_by_name(balance_sheet, ["total debt"]) / self.sum_vectors_by_name(balance_sheet, ["total equity"])

        ### financial (better) method ###
        t2 = calc_adjusted_assets(yearly_income_statement, analysis_group) / analysis_group["adj_equity"]

        return t1,t2

    def calc_ebit(self,
                  income_statement : dict):
        df = pd.DataFrame.from_dict(income_statement)
        # operating_income = df.loc["operating income"]
        net_income_before_tax = df.loc["net income before taxes"]
        operating_interes_exp     = None
        non_operating_interest_exp = None
        try:
            operating_interes_exp = df.loc["interest exp.(inc.),net-operating, total"].fillna(0)
            operating_interes_exp *= -1
            net_income_before_tax += operating_interes_exp
        except:
            pass
        try:
            non_operating_interest_exp = df.loc["interest inc.(exp.),net-non-op., total"].fillna(0)
            non_operating_interest_exp *= -1
            net_income_before_tax += non_operating_interest_exp
        except:
            pass
        return net_income_before_tax


    def calc_operating_margin(self,
                              income_statement : dict,
                              analysis_group : dict):
        """
        calculates operating margin EBIT/renenues
        """
        df = pd.DataFrame.from_dict(income_statement)
        revenue = df.loc["revenue"]
        ebit    = analysis_group["ebit"]

        return ebit / revenue


    def calc_capital_turnover(self,
                              income_statement : dict,
                              analysis_group : dict):

        df = pd.DataFrame.from_dict(income_statement)
        revenue = df.loc["revenue"]
        invested_capital    = analysis_group["invested_capital"]
        bv_invested_capital = analysis_group["bv_invested_capital"]

        bv_capital_turnover = revenue / bv_invested_capital
        capital_turnover    = revenue / invested_capital

        return bv_capital_turnover, capital_turnover


    def calc_ROC(self,
                 analysis_group : dict):


        ebit = analysis_group["ebit"]
        bv_invested_capital = analysis_group["bv_invested_capital"]
        invested_capital    = analysis_group["invested_capital"]

        # reduce dimensions: take all ebit but the oldest, take all invested capital but the latest
        ebit = ebit[:-1]

        bv_invested_capital = bv_invested_capital[1:]
        invested_capital    = invested_capital[1:]

        bv_invested_capital.index = ebit.index
        invested_capital.index    = ebit.index

        ROC    = (1-BUISNESS_TAX_RATE) * ebit / invested_capital
        bv_ROC = (1-BUISNESS_TAX_RATE) * ebit / bv_invested_capital
        return bv_ROC, ROC


    def calc_ROE(self, income_statement : dict, balance_sheet    : dict):

        inc_df = pd.DataFrame.from_dict(income_statement)
        bal_df = pd.DataFrame.from_dict(balance_sheet)

        net_income = inc_df.loc["diluted net income"]
        interest_inc = inc_df.loc["interest inc.(exp.),net-non-op., total"]
        equity     = bal_df.loc["total equity"]
        cash       = bal_df.loc["cash & equivalents"]

        net_income = net_income[:-1]
        interest_inc = interest_inc[:-1]
        cash = cash[:-1]

        equity     = equity[1:]
        equity.index = net_income.index

        ROE = net_income / equity
        noneCashROE = (net_income - interest_inc*(1-BUISNESS_TAX_RATE)) / \
                      (equity - cash)

        return ROE,noneCashROE

    def calc_ROA(self,
                 analysis_group : dict,
                 balance_sheet : dict):


        bal_df = pd.DataFrame.from_dict(balance_sheet)

        ebit = analysis_group["ebit"]
        assets = bal_df.loc["total assets"]

        ebit = ebit[:-1]
        assets = assets[1:]

        assets.index = ebit.index


        return (1-BUISNESS_TAX_RATE) * (ebit / assets)


    ## INTO TO DCF (DEPRICIATED CASH FLOW ##
    def calc_NOPLAT(self,
                    analysis_group : dict,
                    income_statement : dict,
                    ):

        inc_df = pd.DataFrame.from_dict(income_statement)
        ebit = analysis_group["ebit"]
        taxes = inc_df.loc["provision for income taxes"]
        noplat = ebit - taxes
        return noplat

    def calc_FCFF(self,
                  analysis_group : dict,
                  income_statement : dict,
                  cashflow_statement : dict):
        """
        calc free cash flow for firm
        """
        inc_df = pd.DataFrame.from_dict(income_statement)
        cf_df  = pd.DataFrame.from_dict(cashflow_statement)

        ebit = analysis_group["ebit"]
        taxes = inc_df.loc["provision for income taxes"]
        noplat = ebit - taxes

        depreciation = cf_df.loc["depreciation/depletion"]
        capital_exp  = cf_df.loc["capital expenditures"]
        change_in_working_capital = cf_df.loc["changes in working capital"]
        fcff = noplat + depreciation - capital_exp - change_in_working_capital
        return fcff


    def calc_reinvestment_rate(self,
                  analysis_group : dict,
                  income_statement : dict,
                  cashflow_statement : dict):
        inc_df = pd.DataFrame.from_dict(income_statement)
        cf_df  = pd.DataFrame.from_dict(cashflow_statement)

        ebit = analysis_group["ebit"]
        taxes = inc_df.loc["provision for income taxes"]
        noplat = ebit - taxes

        depreciation = cf_df.loc["depreciation/depletion"]
        capital_exp  = cf_df.loc["capital expenditures"]
        change_in_working_capital = cf_df.loc["changes in working capital"]
        rr = (capital_exp - depreciation + change_in_working_capital) / noplat
        return rr


    ### Mains ####
    def calc_assetst(self):

        #### Quarterly analysis ####
        self.Q_analysis["bv_working_capital"] = self.calc_bv_working_capital(self.BAL)
        self.Q_analysis["working_capital"]    = self.calc_working_capital(self.BAL)
        self.Q_analysis["property/plant/equipment"] = self.calc_property_plant_equipment(self.BAL)
        self.Q_analysis["current_r&d_asset"]  = self.calc_depriciated_rnd(self.INC)
        self.Q_analysis["bv_invested_capital"], self.Q_analysis["invested_capital"] = self.calc_invested_capital(self.Q_analysis)
        self.Q_analysis["adj_goodwill_intangibles"] = self.calc_goodwill_intangibles(self.BAL)
        self.Q_analysis["adj_equity"] = self.calc_adjusted_equity(self.Q_analysis, self.BAL)
        self.Q_analysis["ebit"] = self.calc_ebit(self.INC)
        self.Q_analysis["operating_margin"] = self.calc_operating_margin(self.INC, self.Q_analysis)
        self.Q_analysis["bv_capital_turnover"], self.Q_analysis["capital_turnover"] = self.calc_capital_turnover(self.INC, self.Q_analysis)
        self.Q_analysis["bv_roc"], self.Q_analysis["roc"] = self.calc_ROC(self.Q_analysis)
        self.Q_analysis["roe"], self.Q_analysis["non_cash_roe"] = self.calc_ROE(self.INC, self.BAL)
        self.Q_analysis["roa"] = self.calc_ROA(self.Q_analysis, self.BAL)

        # DCF Calculations
        self.Q_analysis["noplat"] = self.calc_NOPLAT(self.Q_analysis, self.INC)
        self.Q_analysis["fcff"] = self.calc_FCFF(self.Q_analysis, self.INC, self.CAS)
        self.Q_analysis["reinvestment_rate"] = self.calc_reinvestment_rate(self.Q_analysis, self.INC, self.CAS)

        #### Yearly analysis ####
        self.K_analysis["bv_working_capital"] = self.calc_bv_working_capital(self.BAL_K)
        self.K_analysis["working_capital"]    = self.calc_working_capital(self.BAL_K)
        self.K_analysis["property/plant/equipment"] = self.calc_property_plant_equipment(self.BAL_K)
        self.K_analysis["current_r&d_asset"]  = self.calc_depriciated_rnd(self.INC_K)
        self.K_analysis["bv_invested_capital"], self.K_analysis["invested_capital"] = self.calc_invested_capital(self.K_analysis)
        self.K_analysis["adj_goodwill_intangibles"] = self.calc_goodwill_intangibles(self.BAL_K)
        self.K_analysis["adj_equity"] = self.calc_adjusted_equity(self.K_analysis, self.BAL_K)
        self.K_analysis["financial_leaverage"] = self.calc_financial_leverage(self.K_analysis, self.BAL_K, self.BAL_K)
        self.K_analysis["ebit"] = self.calc_ebit(self.INC_K)
        self.K_analysis["operating_margin"] = self.calc_operating_margin(self.INC_K, self.K_analysis)
        self.K_analysis["bv_capital_turnover"], self.K_analysis["capital_turnover"] = self.calc_capital_turnover(self.INC_K, self.K_analysis)
        self.K_analysis["bv_roc"], self.K_analysis["roc"] = self.calc_ROC(self.K_analysis)
        self.K_analysis["roe"], self.K_analysis["non_cash_roe"] = self.calc_ROE(self.INC_K, self.BAL_K)
        self.K_analysis["roa"] = self.calc_ROA(self.K_analysis, self.BAL_K)

        # DCF Calculations
        self.K_analysis["noplat"] = self.calc_NOPLAT(self.K_analysis, self.INC_K)
        self.K_analysis["fcff"] = self.calc_FCFF(self.K_analysis, self.INC_K, self.CAS_K)
        self.K_analysis["reinvestment_rate"] = self.calc_reinvestment_rate(self.K_analysis, self.INC, self.CAS)

        return

# TODO : STOPING NOW - ADDING MODULE FOR GET A SUPPLUMNETAL DATA FROM MARKET WATCH

temp_c = CompDataAnalysis("MMM")
temp_c.set_master_data("main_data_temp.pkl")
temp_c.calc_assetst()
# print(temp_c.K_analysis["roe"])
# for i,j in temp_c.BAL["2020-12-31"].items():
#     print(i,j)
# print(temp_c.INC_K)
# print(temp_c.calc_financial_leverage(temp_c.Q_analysis, temp_c.BAL, temp_c.BAL_K))
# for i in temp_c.INC.values():
#     for j in i:
#         print(j)



