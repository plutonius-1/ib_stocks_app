import xml.etree.ElementTree as ET
from datetime import datetime
import re
import requests
import os
import pandas as pd
import time
import pickle
import threading
import logging
import numpy as np

### GENERAL KEYWORDS ###

FINANCIALS = "financials"
HOST = "host"
PORT = "port"
CLIENTID = "clientId"
LAST_UPDATED = "last_updated"
TICKERS = "tickers"

### PATHS ###
DATA_PATH           = "./data/"

RAW_DATA_PATH       = DATA_PATH + "raw_data/"
PROCESSED_DATA_PATH = DATA_PATH + "processed_raw_data/"
COMPANY_ANALYSIS_PATH = DATA_PATH + "companies_analysis/"
MARKET_RESEARCH_PATH  = DATA_PATH + "market_research/"
DEEP_COMPERATIVE_PATH = DATA_PATH + "deep_comperative_analysis/"

IB = "IB"
IB_REQUEST_HISTORY_PATH = "./ib_req_histroy.pkl"
IB_DATA_PATH       = RAW_DATA_PATH + "ib_data/"
IB_PROCESSED_PATH  = PROCESSED_DATA_PATH + "ib_data/"
IB_FINANCIALS_PATH = IB_DATA_PATH

SICS_DIR_PATH = "./SICS/"
BASIC_APP_STURCTURE_DIRS = [RAW_DATA_PATH, PROCESSED_DATA_PATH, COMPANY_ANALYSIS_PATH, MARKET_RESEARCH_PATH, DEEP_COMPERATIVE_PATH, IB_DATA_PATH, IB_PROCESSED_PATH, SICS_DIR_PATH]
    # SICs
SIC_CODES_PATH = SICS_DIR_PATH + "sic_codes.pkl"
SIC_DICIONARY_PATH = SICS_DIR_PATH + "dictionary.pkl"

##################
SNAPSHOT_POSTFIX = "_snapshot.xml"

### RATIOS CONTS ###
MKTCAP    = "MKTCAP"
VOL10DAVG = "VOL10DAVG"
EV        = "EV"
# PER SHARE DATA #
TTMREVPS  = "TTMREVPS" # rev per share
QBVPS     = "QBVPS" # book val per share
QCSHPS    = "QCSHPS"
TTMCFSHR  = "TTMCFSHR"
TTMDIVSHR = "TTMDIVSHR"

# OTHER RATIOS #
TTMGROSMGN = "TTMGROSMGN"
TTMROEPCT  = "TTMROEPCT"
TTMPR2REV  = "TTMPR2REV"
PEEXCLXOR  = "PEEXCLXOR"
PRICE2BK   = "PRICE2BK"
COMPARISON_PARAMS = [MKTCAP, VOL10DAVG, EV, TTMREVPS, QBVPS, QCSHPS, TTMCFSHR,
                          TTMDIVSHR,TTMGROSMGN, TTMROEPCT, TTMPR2REV, PEEXCLXOR, PRICE2BK]

MKTCAP_TOTAL = "MKTCAP_TOTAL"
MKTSHARE     = "MKTSHARE"

## IbTWS stuff ##
GET_FUNDUMENTALS = "fundumentals"
IBTWS_FUNCTIONS = [GET_FUNDUMENTALS]
IB_MAX_REQUESTS_PER_SEC = 50
IB_MAX_REQUESTS_PER_10_MIN = 60
IB_COMPARISON_PARAMS = [MKTCAP, VOL10DAVG, EV, TTMREVPS, QBVPS, QCSHPS, TTMCFSHR,
                          TTMDIVSHR,TTMGROSMGN, TTMROEPCT, TTMPR2REV, PEEXCLXOR, PRICE2BK]

## Historical cfgs ##
GET_HISTORICAL_DATA = "hist"
DURATION_UNITS_KW = "durationUnits"
DURATION_KW       = "duration"

HIST_VALID_DURATION_UNITS = ["S","D","W","M","W"]
BARSIZE_SETTING_KW = "barSizeSetting"
BARS_NUM_KW = "barsNum"
HIST_VALID_BAR_SIZES      = {"SEC":[1,5,10,15,30],
                             "MIN":[1,2,3,5,10,15,20,30],
                             "HOU":[1,2,3,4,8],
                             "DAY":[1],
                             "WEEK":[1],
                             "MON":[1]}
WHAT_TO_KNOW_KW = "whatToShow"
HIST_DATA_TYPES = ["TRADES","MIDPOINT","BID","ASK","BID_ASK","ADUJST_LAST","HISTORICAL_VOLATILITY","OPTION_IMPLIED_VOLATILITY","REBATE_RATE","FEE_RATE","YIELD_BID","YIELD_ASK","YIELD_BID_ASK","YIELD_LAST"]
IBTWS_FUNCTIONS = [GET_FUNDUMENTALS, GET_HISTORICAL_DATA]

## News cfgs ##
GET_HISTORICAL_NEWS = "hist_news"
START_DATE_KW = "startDate"
END_DATE_KW   = "endDate"

GET_NEWS_PROVIDERS = "news_providers"

## Contracts cfgs ##
GET_CONTRACT_DETAILS = "reqContractDetails"

#################

### PROCESSED XML FILES POSTFIX ###
FUND_REQ_TYPES_DICT = {
    "ReportsFinStatements" : "financial_statements.xml",
    "ReportSnapshot"       : "snapshot.xml",
    "ReportsFinSummary"    : "financial_summary.xml",
    "RESC"                 : "analysts.xml"
}



PROCESSED_FUNDAMENTAL_XML = "_processed_fundamental"
PROCESSED_SNAPSHOT_XML    = "_processed_snapshot"
PROCESSED_FINSUMMERY_XML  = "_processed_finsummery"
PROCESSED_OVERVIEW_XML    = "_processed_overview"

### GENERAL ###
FUNDAMENTALS = "fundamentals"
SNAPSHOT     = "snapshot"


###########################


## GENERAL CONSTS ##
ANALYZE = "analyze"
Q       = "Q"
K       = "K"
Q_data  = "Q_data"
K_data  = "K_data"

INCOME_NAME = "INC"
BALACNE_NAME = "BAL"
CASHFLOW_NAME = "CAS"
STATEMENTS_NAMES = [INCOME_NAME, BALACNE_NAME, CASHFLOW_NAME]
### DATE FORMAT ###
RE_DATE_FORMAT = r'\d{4}-\d{2}-\d{2}'
re_date_format = re.compile(RE_DATE_FORMAT)
DEFAULT_OBJECT_LAST_UPDATE = "0000-00-00"
DEFAULT_IB_REQ_HISTORY_DICT = {"LAST_REQ_TIME":None,
                               "REQS":IB_MAX_REQUESTS_PER_10_MIN}

SOURCES_COMPER_PARAMS = {
    IB : IB_COMPARISON_PARAMS
}
