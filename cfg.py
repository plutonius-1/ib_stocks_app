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

### GENERAL KEYWORDS ###

FINANCIALS = "financials"
HOST = "host"
PORT = "port"
CLIENTID = "clientId"
LAST_UPDATED = "last_updated"

### PATHS ###
DATA_PATH           = "./data/"

RAW_DATA_PATH       = DATA_PATH + "raw_data/"
PROCESSED_DATA_PATH = DATA_PATH + "processed_raw_data/"
COMPANY_ANALYSIS_PATH = DATA_PATH + "companies_analysis/"
MARKET_RESEARCH_PATH  = DATA_PATH + "market_research/"
DEEP_COMPERATIVE_PATH = DATA_PATH + "deep_comperative_analysis/"

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


## IbTWS stuff ##
GET_FUNDUMENTALS = "fundumentals"
IBTWS_FUNCTIONS = [GET_FUNDUMENTALS]
IB_MAX_REQUESTS_PER_SEC = 50
IB_MAX_REQUESTS_PER_10_MIN = 60
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

## GENERAL CONSTS ##
ANALYZE = "analyze"

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
