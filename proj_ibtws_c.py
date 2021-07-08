import cfg
from cfg import pd
import datetime
from uuid import uuid1
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
import proj_req_id_handler_c
import proj_utils

class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestWrapper(wrapper.EWrapper):
    def __init__(self):
        wrapper.EWrapper.__init__(self)

    def currentTime(self, time:int):
        super().currentTime(time)
        print("CurrentTime:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"))

class IBreq:
    """
    Holds a general data of a request from IB
    """
    def __init__(self,
                 reqId : int,
                 reqType : str,
                 symbol = None,
                 contract = None):
        self.reqId = reqId
        self.symbol = symbol
        self.contract = contract
        self.reqType = reqType

    def __str__(self):
        return "IBreq Object ** reqId : {}, symbol : {}, reqType : {}".format(self.reqId, self.symbol, self.reqType)

######### Consts End ########
# where to save data from IB based on its type
generalReqTypeDict = {
    "financials" : cfg.IB_FINANCIALS_PATH
}

# if requests was financial, get the postfix based on the type of request: ticker_postfix
# fundReqTypesDict = {
    # "ReportsFinStatements" : "financial_statements.xml",
    # "ReportSnapshot"       : "snapshot.xml",
    # "ReportsFinSummary"    : "financial_summary.xml",
    # "RESC"                 : "analysts.xml"
# }
fundReqTypesDict = cfg.FUND_REQ_TYPES_DICT

class IbTws(TestWrapper,
            TestClient):

    def __init__(self, **kwargs):
        TestWrapper.__init__(self)
        TestClient.__init__(self, wrapper = self)
        self.id_handler = proj_req_id_handler_c.Req_id_handler_c()

        # local consts
        self.TICKER_KEY = "ticker"
        self.HOST_KEY   = "host"
        self.PORT_KEY   = "port"
        self.CLIENT_ID  = "clientId"


        # self.function = function
        self.outGoingRequests = {}
        self.kwargs = kwargs
        self.host = kwargs[self.HOST_KEY]
        self.port = kwargs[self.PORT_KEY]
        self.clientId = kwargs[self.CLIENT_ID]

        # some init assertions ##
        # assert self.function != None
        # assert self.function in cfg.IBTWS_FUNCTIONS
        # connetion assertion
        assert self.connectToTWS(self.host, self.port, self.clientId), "*** Exit: TWS not connected ***"

    def _run_(self):
        self.run()

    ### Error Handling ###
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
            super().error(reqId, errorCode, errorString)
            print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
            _id = int(reqId)
            if (_id in self.id_handler.outgoing_reqs):
                self.id_handler.response_id(_id)

    ### reqId Handlers ###
    def makeUUID(self):
        return int(uuid1())

    def reqCallBackHandler(self, reqId):
        key = str(int(reqId))
        if key in self.outGoingRequests:
            del self.outGoingRequests[key]
        return

    def reqIdRegister(self, reqId , reqType : str, symbol : str):
        key = str(int(reqId))
        # assert key not in self.outGoingRequests, "a new request was made while reqId {} did not return".format(reqId)
        reqIdObj = IBreq(reqId, reqType, symbol)
        self.outGoingRequests.update({key : reqIdObj})

    ######################
    def _check_max_requests(self):
        while self.id_handler.get_num_outgoing_reqs() >= cfg.IB_MAX_REQUESTS_PER_SEC - 1: # and
              # self.id_handler:
            proj_utils.print_warning_msg(f"Holding on request - reached max request per second limit {cfg.IB_MAX_REQUESTS_PER_SEC}")
            cfg.time.sleep(1)

    def call_function(self, function, **kwargs):
        # before sending request to IB - first check the outstanding number of requests is not bigger the the allowed max (07/08/21): 50

        if (function == cfg.GET_FUNDUMENTALS):
            try:
                ticker = self.kwargs[self.TICKER_KEY]
            except:
                ticker = kwargs[self.TICKER_KEY]

            contract = self.make_us_stk_contract(ticker)
            # reqIds = [self.makeUUID() for i in range(4)]
            reqIds = [self.id_handler.register_outgoing_req() for i in range(4)]
            self.reqFundamentalData(reqIds[0], contract, "ReportsFinStatements", [])
            self.reqFundamentalData(reqIds[1], contract, "ReportSnapshot", [])
            self.reqFundamentalData(reqIds[2], contract, "ReportsFinSummary", [])
            self.reqFundamentalData(reqIds[3], contract, "RESC",[])
        else:
            pass




    ################### OVERRIDES ###################
    ### fundumentals overrides ###
    def reqFundamentalData(self,
                           reqId : int,
                           contract : Contract,
                           reportType : str,
                           fundamentalDataOptions : list
                           ):
        super().reqFundamentalData(reqId, contract, reportType, fundamentalDataOptions)
        print("ReqId: {} Requesting :{} Fundumental data type :{}".format(reqId,contract.symbol, reportType))
        self.reqIdRegister(reqId, reportType, symbol = contract.symbol)

    def fundamentalData(self, reqId: TickerId, data: str):
        super().fundamentalData(reqId, data)
        self.save_general_file(reqId = reqId,
                               type_to_save = cfg.FINANCIALS,
                               data = data)
    ################################# End fundamentals overrides


    ################### UTILS ###################
    def save_general_file(self,
                          reqId,
                          type_to_save : str,
                          data):
        """
        @ param - reqId
        @ param - type_to_save: in which dir to save data based on request type (see generalReqTypeDict for options
        """
        # convert the reqId to str - Note key should be strings
        reqIdKey = int(reqId)
        assert str(reqIdKey) in self.outGoingRequests, "ERROR: reqId: {} not in outGoingRequests".format(reqIdKey)

        # get the req object
        reqIdObj = self.outGoingRequests[str(reqIdKey)]
        reqType = reqIdObj.reqType
        symbol  = reqIdObj.symbol

        # get the right postfix
        if (type_to_save == cfg.FINANCIALS):
            reqType = fundReqTypesDict[reqType]

        print("*** Saving ", reqIdObj, " ***")
        filename = symbol + "_" + reqType

        # get the path to save the file to
        path_to_save = generalReqTypeDict[type_to_save] + symbol.upper() + "/"

        # make sure dir exists
        proj_utils.check_dir_exists(path_to_save)

        # save
        f = open(path_to_save + filename, "w")
        f.write(data)
        f.close()

        # delete from reqIds bank
        self.reqCallBackHandler(str(reqIdKey))
        self.id_handler.response_id(reqId)

    def connectToTWS(self, host : str, port : str, clientId : int):
        try:
            self.connect(host, port, clientId)
        except:
            pass

        if not self.isConnected():
            print("IbTws_c is not connected")
            return False
        return True

    def make_us_stk_contract(self, ticker : str):
        ticker = (str(ticker)).upper()
        contract = Contract()
        contract.symbol = ticker
        contract.currency = "USD"
        contract.exchange = "SMART"
        contract.secType = "STK"
        return contract

    def wait_for_api_task(self, msg = ""):
        """
        @ param msg - the main reason why we are halting the process of the software
        function halts the process while wating for IB API to finish the while response
        """
        e_time = 0
        while self.id_handler.waiting_for_response:
            if (e_time % 10 == 0 or e_time == 0):
                print(proj_utils.bcolors.OKGREEN + msg + ": slept for {}".format(e_time) + proj_utils.bcolors.ENDC)
                print("ids left: ", self.id_handler.outgoing_reqs)
            cfg.time.sleep(1)
            e_time += 1
