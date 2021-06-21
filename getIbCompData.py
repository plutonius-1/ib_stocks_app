# import argparse
# import datetime
# import collections
# import inspect

# import logging
# import time
# import os
# import sys

# from ibapi import wrapper
# from ibapi import utils
# from ibapi.client import EClient
# from ibapi.utils import iswrapper

# from ibapi.common import * # @UnusedWildImport
# from ibapi.order_condition import * # @UnusedWildImport
# from ibapi.contract import * # @UnusedWildImport
# from ibapi.order import * # @UnusedWildImport
# from ibapi.order_state import * # @UnusedWildImport
# from ibapi.execution import Execution
# from ibapi.execution import ExecutionFilter
# from ibapi.commission_report import CommissionReport
# from ibapi.ticktype import * # @UnusedWildImport
# from ibapi.tag_value import TagValue

# from ibapi.account_summary_tags import *

# import xml.etree.ElementTree as ET

# ########## Consts ############
# # IB Dirs paths
# IB_FINANCIALS_PATH = "./ib_data/financials/"


# FINANCIALS = "financials"
# ######### Consts End ########
# # where to save data from IB based on its type
# generalReqTypeDict = {
    # "financials" : IB_FINANCIALS_PATH
# }

# # if requests was financial, get the postfix based on the type of request: ticker_postfix
# fundReqTypesDict = {
    # "ReportsFinStatements" : "financial_statements.xml",
    # "ReportSnapshot"       : "snapshot.xml",
    # "ReportsFinSummary"    : "financial_summary.xml",
    # "RESC"                 : "analysts.xml"
# }

# class IBreq:
    # """
    # Holds a general data of a request from IB
    # """
    # def __init__(self,
                 # reqId : int,
                 # reqType : str,
                 # symbol = None,
                 # contract = None):
        # self.reqId = reqId
        # self.symbol = symbol
        # self.contract = contract
        # self.reqType = reqType

    # def __str__(self):
        # return "IBreq Object ** reqId : {}, symbol : {}, reqType : {}".format(self.reqId, self.symbol, self.reqType)


# class TestClient(EClient):
    # def __init__(self, wrapper):
        # EClient.__init__(self, wrapper)


# class TestWrapper(wrapper.EWrapper):
    # def __init__(self):
        # wrapper.EWrapper.__init__(self)

    # def currentTime(self, time:int):
        # super().currentTime(time)
        # print("CurrentTime:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"))

# class TestApp(TestWrapper, TestClient):
    # def __init__(self):
        # TestWrapper.__init__(self)
        # TestClient.__init__(self, wrapper = self)
        # self.outGoingRequests = {}

    # ### reqId Handlers ###
    # def reqCallBackHandler(self, reqId):
        # key = str(int(reqId))
        # if key in self.outGoingRequests:
            # del self.outGoingRequests[key]
        # return

    # def reqIdRegister(self, reqId , reqType : str, symbol : str):
        # key = str(int(reqId))
        # assert key not in self.outGoingRequests, "a new request was made while reqId {} did not return".format(reqId)
        # reqIdObj = IBreq(reqId, reqType, symbol)
        # self.outGoingRequests.update({key : reqIdObj})
        # # print("outGoingRequests: \n", self.outGoingRequests)
    # ######################

    # def error(self, reqId: TickerId, errorCode: int, errorString: str):
            # super().error(reqId, errorCode, errorString)
            # print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)


    # @iswrapper
    # def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       # currency: str):
        # super().accountSummary(reqId, account, tag, value, currency)
        # print("AccountSummary. ReqId:", reqId, "Account:", account,
              # "Tag: ", tag, "Value:", value, "Currency:", currency)

    # @iswrapper
    # def currentTime(self, time:int):
        # super().currentTime(time)
        # print("CurrentTime:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"))


    # ### fundumentals overrides ###
    # def reqFundamentalData(self,
                           # reqId : int,
                           # contract : Contract,
                           # reportType : str,
                           # fundamentalDataOptions : list
                           # ):
        # super().reqFundamentalData(reqId, contract, reportType, fundamentalDataOptions)
        # print("Requesting :{} Fundumental data type :{}".format(contract.symbol, reportType))
        # self.reqIdRegister(reqId, reportType, symbol = contract.symbol)

    # def fundamentalData(self, reqId: TickerId, data: str):
        # super().fundamentalData(reqId, data)
        # self.save_general_file(reqId = reqId,
                               # type_to_save = FINANCIALS,
                               # data = data)
    # ################################# End fundamentals overrides

    # def marketDataType(self, reqId: TickerId, marketDataType: int):
        # super().marketDataType(reqId, marketDataType)
        # print("MarketDataType. ReqId:", reqId, "Type:", marketDataType)

    # ### Utils ###
    # def save_general_file(self,
                          # reqId,
                          # type_to_save : str,
                          # data):
        # """
        # @ param - reqId
        # @ param - type_to_save: in which dir to save data based on request type (see generalReqTypeDict for options
        # """
        # # convert the reqId to str - Note key should be strings
        # reqIdKey = str(int(reqId))
        # assert reqIdKey in self.outGoingRequests, "ERROR: reqId: {} not in outGoingRequests".format(reqIdKey)

        # # get the req object
        # reqIdObj = self.outGoingRequests[reqIdKey]
        # reqType = reqIdObj.reqType
        # symbol  = reqIdObj.symbol

        # # get the right postfix
        # if (type_to_save == FINANCIALS):
            # reqType = fundReqTypesDict[reqType]

        # print("*** Saving ", reqIdObj, " ***")
        # filename = symbol + "_" + reqType

        # # get the path to save the file to
        # path_to_save = generalReqTypeDict[type_to_save]

        # # save
        # f = open(path_to_save + filename, "w")
        # f.write(data)
        # f.close()

        # # delete from reqIds bank
        # self.reqCallBackHandler(reqIdKey)

# # TODO - flow:
# # 1) get all differnt sics from a compay overview
# # 2) got to sec search bar https://www.sec.gov/cgi-bin/srch-edgar?text=ASSIGNED-SIC%3D3743+and+FORM-TYPE%3D10-Q&first=2021&last=2021 and download relevant companies data from IB
# # 3) update local SIC dic

# def main():
    # app = TestApp()

    # if (sys.platform == "linux"):
        # host = "192.168.0.100"
    # else:
        # host = "192.168.0.190"

    # app.connect(host = "10.10.4.166", port = 7496, clientId = 10)
    # if (app.isConnected()):

        # contract = Contract()
        # contract.symbol = "MMM"
        # contract.exchange = "NYSE"
        # contract.secType = "STK"
        # print(" ******* Connected *******")
        # #app.reqAccountSummary(0,"All","accountountType")
        # #app.reqMktData(1000, contract, "", False, False, [])
        # app.reqFundamentalData(8001, contract, "ReportsFinStatements", [])
        # app.reqFundamentalData(8002, contract, "ReportSnapshot", [])
        # app.reqFundamentalData(8003, contract, "ReportsFinSummary", [])
        # # app.reqFundamentalData(8004, contract, "ReportsRatios", []) # TODO - not working
        # app.reqFundamentalData(8005, contract, "RESC",[])
        # app.reqCurrentTime()
        # # if (app.isConnected()):
            # # app.disconnect()
            # # print("Connected")
        # app.run()

# if __name__ == "__main__":
    # main()
