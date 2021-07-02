import argparse
import datetime
import collections
import inspect

import logging
import time
import os
import sys

from ibapi import wrapper
from ibapi import utils
from ibapi.client import EClient
from ibapi.utils import iswrapper

from ibapi.common import * # @UnusedWildImport
from ibapi.order_condition import * # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from ibapi.order import * # @UnusedWildImport
from ibapi.order_state import * # @UnusedWildImport
from ibapi.execution import Execution
from ibapi.execution import ExecutionFilter
from ibapi.commission_report import CommissionReport
from ibapi.ticktype import * # @UnusedWildImport
from ibapi.tag_value import TagValue

from ibapi.account_summary_tags import *

import xml.etree.ElementTree as ET


class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestWrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)

    def currentTime(self, time:int):
        super().currentTime(time)
        print("CurrentTime:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"))

class TestApp(TestWrapper, TestClient):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper = self)



    def error(self, reqId: TickerId, errorCode: int, errorString: str):
            super().error(reqId, errorCode, errorString)
            print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)


    @iswrapper
    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        print("AccountSummary. ReqId:", reqId, "Account:", account,
              "Tag: ", tag, "Value:", value, "Currency:", currency)

    @iswrapper
    def currentTime(self, time:int):
        super().currentTime(time)
        print("CurrentTime:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"))


    def marketDataType(self, reqId: TickerId, marketDataType: int):
        super().marketDataType(reqId, marketDataType)
        print("MarketDataType. ReqId:", reqId, "Type:", marketDataType)

    def fundamentalData(self, reqId: TickerId, data: str):
        super().fundamentalData(reqId, data)
        # print("FundamentalData. ReqId:", reqId, "Data:", data)
        print("saving fundamental data")
        # mydata = ET.tostring(data)
        myfile = open("items_aapl.xml", "w")
        myfile.write(data)

app = TestApp()

if (sys.platform == "linux"):
    host = "192.168.0.100"
else:
    host = "192.168.0.190"

app.connect(host = host, port = 7496, clientId = 10)
if (app.isConnected()):

    contract = Contract()
    contract.symbol = "TPB"
    contract.exchange = "NYSE"
    contract.secType = "STK"
    print(" ******* Connected *******")
    #app.reqAccountSummary(0,"All","accountountType")
    #app.reqMktData(1000, contract, "", False, False, [])
    app.reqFundamentalData(8001, contract, "ReportsFinStatements", [])

    app.reqCurrentTime()
    app.run()
    if (app.isConnected()):
        print("Connected")
        app.disconnect()
