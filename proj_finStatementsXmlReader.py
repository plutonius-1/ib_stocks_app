# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 15:29:11 2021

@author: avsha
"""

import xml.etree.ElementTree as ET
import pandas as pd
import pickle
import cfg

########### TAGS #############

COIDS = "CoIDs"
ISSUES = "issues"

##############################

class finStatementsXmlReader_c:
    def __init__(self):
        self.xml_master_root = None
        self.ticker = None
        self._map_dic = None
        self._BAL_K = None
        self._INC_K = None
        self._CAS_K = None
        self._BAL_Q = None
        self._INC_Q = None
        self._CAS_Q = None

    ##### PUBLIC ####

    def set_xml_master_root(self, path_to_xml):

        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        self.xml_master_root = root

    def set_ticker(self, ticker):
        self.ticker = ticker
        self.set_xml_master_root(cfg.IB_FINANCIALS_PATH + self.ticker + "_financial_statements.xml")

    def get_balance_sheet(self):
        return self.BAL

    def get_income_statement(self):
        return self.INC

    def get_cash_flow(self):
        return self.CAS

    def prase_data(self):
        try:
            self._map_dic = self._get_dic_mapping_element(self.xml_master_root)
            Q_data,  K_data = self._prase_comp_data(self.xml_master_root, self._map_dic)
            self._BAL_Q = Q_data["BAL"]
            self._CAS_Q = Q_data["CAS"]
            self._INC_Q = Q_data["INC"]
            self._BAL_K = K_data["BAL"]
            self._CAS_K = K_data["CAS"]
            self._INC_K = K_data["INC"]
            data = {"Q_data":Q_data, "K_data":K_data}
            name = self.get_ticker(self.xml_master_root).upper()
            name = name + cfg.PROCESSED_FUNDAMENTAL_XML
            path = cfg.IB_FINANCIALS_PATH
            self.save_obj(data, path + name) # saves as pkl
            return data
        except:
            return None

    def save_obj(self, obj, name ):
        with open(name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name ):
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)

    def get_fundamentals_obj(self):
        return self.prase_data()

    def get_ticker(self, xml_root):
        try:
            ticker = xml_root.find("./Issues/Issue/IssueID[@Type='Ticker']").text
        except:
            ticker = None

        assert ticker != None, "could not found ticker info in XML file"
        return str(ticker)

    #### PRIVATE ####

    def _raise_err(self,
                   _type = "",
                   _exp  = "",
                   _actual = ""):

        raise "got {} type : {} - expected : {}".format(_type, _actual, _exp)


    def _get_dic_mapping_element(self,
                                 xml_root):

        d = {"CAS":{}, "BAL":{}, "INC":{}}
        COAMap = xml_root.find("./FinancialStatements/COAMap")

        if (COAMap == None): raise "no COAMap tag found"

        for map_item in COAMap:
            attrib = map_item.attrib
            short_name     = attrib["coaItem"]
            statement_type = attrib["statementType"]
            line_id        = attrib["lineID"]
            precision      = attrib["precision"]
            name           = map_item.text


            dd = {
                    "short_name":short_name,
                    "full_name":name,
                    "statement_type":statement_type,
                    "line_id":line_id,
                    "precision":precision
                }
            d[statement_type].update({short_name:dd})

        return d


    def _find_code_name_mapping(self,
                                sheet_type,
                                code_name,
                                mapping_dic):


        res = mapping_dic[sheet_type][code_name]["full_name"]
        # print(mapping_dic[sheet_type][code_name])
        if res == None:
            raise_err("code mapping", code_name, "NA")

        return res


    def _prase_statement(self,
                         statement,
                         date,
                         mapping_dic : dict,
                         sheet_type : str):

        statement_type = statement.attrib["Type"]

        res = {statement_type : {date : {}}}


        # check type validity
        if (statement_type != sheet_type):
            pass
            # raise_err("statement type", sheet_type, statement_type)

        for line in statement:
            if (line.tag == "lineItem"):
                code_name = line.attrib["coaCode"]
                actual_name = self._find_code_name_mapping(sheet_type, code_name, mapping_dic)
                actual_name = actual_name.lower()
                res[statement_type][date].update({actual_name:float(line.text)})

        return res


    def _prase_comp_data(self,
                         xml_root,
                         mapping_dic):
        """

        Parameters
        ----------
        xml_root : elementTree object
            root the the IB fundumentals object as ET.
        mapping_dic :
            mapping of code names to full names.

        Raises
        ------

            DESCRIPTION.

        Returns
        -------
        parsed_data : TYPE - dict of {BAL:{}, INC:{}, CAS:{}}
            DESCRIPTION.

        """
        InterimPeriods = xml_root.find("./FinancialStatements/InterimPeriods")
        AnnualPeriods  = xml_root.find("./FinancialStatements/AnnualPeriods")

        parsed_data_Q = {"INC" : {},
                         "BAL" : {},
                         "CAS" : {}}

        parsed_data_K = {"INC" : {},
                         "BAL" : {},
                         "CAS" : {}}

        if InterimPeriods == None: raise "did not find InterimPeriods in financial statements"

        for InterimPeriod in InterimPeriods:

            date = InterimPeriod.attrib["EndDate"]


            for i in InterimPeriod:

                # get the type first (cash, balance, income)
                statemet_type = i.attrib["Type"]

                # general statement prase
                temp_data = self._prase_statement(i, date, mapping_dic, statemet_type)
                parsed_data_Q[statemet_type].update({date : temp_data[statemet_type][date]})

        for AnnualPeriod in AnnualPeriods:

            date = AnnualPeriod.attrib["EndDate"]


            for i in AnnualPeriod:

                # get the type first (cash, balance, income)
                statemet_type = i.attrib["Type"]

                # general statement prase
                temp_data = self._prase_statement(i, date, mapping_dic, statemet_type)
                parsed_data_K[statemet_type].update({date : temp_data[statemet_type][date]})


        # df = pd.DataFrame(data = parsed_data["BAL"])
        return parsed_data_Q, parsed_data_K


# temp_c = finStatementsXmlReader()
# temp_c.set_xml_master_root("items_aapl.xml")
# temp_c.prase_data()
# root = temp_c.xml_master_root
# for i in root.find("FinancialStatements/InterimPeriods/FiscalPeriod/Statement"):
#     print(i.tag, i.attrib)
#yealy_kesy = temp_c._INC_K["2020-12-31"].keys()
#q_keys = temp_c._INC_Q["2020-12-31"].keys()
# for i in temp_c._BAL_Q["2020-12-31"].keys():
#     print(i)
