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
from dateutil import parser as datetime_parser

from ibapi.account_summary_tags import *
import proj_req_id_handler_c
import proj_utils
import proj_BarData_c

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

        self._newsProviders = None

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

        #========================
        # Field: _temp_bars_data_obj
        # Description - used for hold a temp BarsData object
        self._temp_bars_data_obj = None

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
                print(f"deleting id {_id} to to err")
                self.id_handler.del_from_out_going_reqs(_id)

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
            reqIds = [self.id_handler.register_outgoing_req(historical = True) for i in range(4)]
            self.reqFundamentalData(reqIds[0], contract, "ReportsFinStatements", [])
            self.reqFundamentalData(reqIds[1], contract, "ReportSnapshot", [])
            self.reqFundamentalData(reqIds[2], contract, "ReportsFinSummary", [])
            self.reqFundamentalData(reqIds[3], contract, "RESC",[])
            # self.reqFundamentalData(reqIds[4], contract, "Ratios", [])

        elif (function == cfg.GET_HISTORICAL_DATA):

            ticker = kwargs[self.TICKER_KEY]
            contract = self.make_us_stk_contract(ticker)

            durationUnits = kwargs[cfg.DURATION_UNITS_KW]
            duration      = kwargs[cfg.DURATION_KW]

            # Duration Processing #
            durationUnits_time_delta = {"S" : datetime.timedelta(days=int(duration)),
                                        "D" : datetime.timedelta(seconds=int(duration)),
                                        "W" : datetime.timedelta(weeks=int(duration)),
                                        "M" : datetime.timedelta(weeks=(int(duration) * 4)),
                                        "Y" : datetime.timedelta(weeks=(int(duration) * 52))}
            queryTime = (datetime.datetime.today() - durationUnits_time_delta[durationUnits]).strftime("%Y%m%d %H:%M:%S")

            whatToShow = kwargs[cfg.WHAT_TO_KNOW_KW]

            # Bars Processing #
            barsNum      = kwargs[cfg.BARS_NUM_KW]
            barSizeUnits = kwargs[cfg.BARSIZE_SETTING_KW]
            if (barSizeUnits in ["sec","min","hour"] and (int(barsNum) > 1)):
                barSizeUnits += "s"



            reqIds = [self.id_handler.register_outgoing_req(historical = True)]

            # start a temp histrocial object
            self._temp_bars_data_obj = proj_BarData_c.bars_data_objects_by_type[whatToShow]
            self._temp_bars_data_obj.set_ticker(ticker)

            super().reqHistoricalData(
                reqId = reqIds[0],
                contract = contract,
                endDateTime = queryTime,
                durationStr = f"{duration} {durationUnits}",
                barSizeSetting = f"{barsNum} {barSizeUnits}",
                whatToShow = kwargs[cfg.WHAT_TO_KNOW_KW],
                useRTH = 0,
                formatDate = 1,
                keepUpToDate = False,
                chartOptions = []) # TODO add the TRUE case option as well

        elif (function == cfg.GET_NEWS_PROVIDERS):
            print("Asking for news providers...")
            self.reqNewsProviders()
            while self._newsProviders == None:
                cfg.time.sleep(1)

        elif (function == cfg.GET_HISTORICAL_NEWS):

            # define ticker
            ticker = kwargs[self.TICKER_KEY]

            # First update the local copy of newProviders object
            self.call_function(cfg.GET_NEWS_PROVIDERS)
            # self.wait_for_api_task("Wating to recive news providers")
            cfg.time.sleep(10)

            # also get the contract details for contract number
            # note that GET_CONTRACT_DETAILS has a wait task inside
            conId = self.call_function(cfg.GET_CONTRACT_DETAILS, ticker = ticker).conId

            # prepre the rest needed parametrs
            # according to spec providers should be "+" seperated list
            newsProvidersCodes = "+".join([str(i.code) for i in self._newsProviders])
            startDate = self.format_date_time(kwargs[cfg.START_DATE_KW])
            endDate   = self.format_date_time(kwargs[cfg.END_DATE_KW])
            reqIds = [self.id_handler.register_outgoing_req(historical = True)]
            super().reqHistoricalNews(
                reqId = reqIds[0],
                conId = conId,
                providerCodes = newsProvidersCodes,
                startDateTime = startDate,
                endDateTime   = endDate,
                totalResults  = 300,
                historicalNewsOptions = []
            )

        elif (function == cfg.GET_CONTRACT_DETAILS):
            ticker   = kwargs[self.TICKER_KEY]
            contract = self.make_us_stk_contract(ticker)
            reqIds = [self.id_handler.register_outgoing_req(historical = True)]
            cd = self.reqContractDetails(reqIds[0], contract)
            return cd

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

    def scannerParameters(self, xml : str):
        super().scannerParameters(xml)
        open("scanner.xml", "w").write(xml)
        print("ScannerParameters recived")

    #====================================
    ### Historical Data Overrides ###
    def historicalData(self, reqId:int, bar: BarData):
        print(f'{__name__}: got historical data for ReqId {reqId}, \n{bar}')
        tmp_bar_data = proj_BarData_c.Bar_data_c(bar)
        self._temp_bars_data_obj.add_bar_data(tmp_bar_data)

    def historicalDataEnd(self, reqId : int, start : str, end : str):
        print(f'{__name__}: finished getting bars ')
        assert self._temp_bars_data_obj is not None

        print(f'{__name__}: object_bars lenth = {len(self._temp_bars_data_obj.get_bars_data())}')
        self._temp_bars_data_obj.save_bars_data()
        self._temp_bars_data_obj = None

    #====================================
    ### News overrides ###
    def reqNewsProviders(self):
        super().reqNewsProviders()
        return

    def newsProviders(self, newsProviders:ListOfNewsProviders):
        print(f'Recived News Providers: {newsProviders}')
        self._newsProviders = newsProviders


    def historicalNews(self, requestId:int, time:str, providerCode:str, articleId:str, headline:str):
        print(f"HISTORICAL HEAD LINE:\ntime{time}\narticleId:{articleId}\nheadline:{headline}")

    ### Contracts overrides ###
    def reqContractDetails(self, reqId:int, contract: Contract):
        super().reqContractDetails(reqId = reqId,
                                   contract = contract)

        self._temp_contract_detail_q = []
        self.wait_for_api_task(msg = "sent request for contract details - waiting for response")
        cfg.time.sleep(1)
        assert len(self._temp_contract_detail_q) == 1
        cd = self._temp_contract_detail_q.pop()
        return cd.contract



    def contractDetails(self, reqId : int, contractDetails : ContractDetails):
        print("Recived Contract details")
        assert len(self._temp_contract_detail_q) == 0
        self._temp_contract_detail_q.append(contractDetails)


        # delete from reqIds bank TODO - make this into a function!
        #self.reqCallBackHandler(str(reqIdKey))
        self.id_handler.response_id(reqId)
        return contractDetails
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
        # while (not self.isConnected()):
            # cfg.time.sleep(1)
            # print(f"{__name__} : Sleeping while ibapi is connectin")
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

    def format_date_time(self, date : str, pattern = "%Y-%m-%d %H:%M%S.0"):
        formated_date = datetime_parser.parse(date)
        formated_date = formated_date.strftime(pattern)
        return formated_date

    def get_news_providers(self):
        return self._newsProviders
