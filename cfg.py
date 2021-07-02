import xml.etree.ElementTree as ET
import requests
import os
import pandas as pd
import time
import pickle

### GENERAL KEYWORDS ###

FINANCIALS = "financials"

### PATHS ###
DATA_PATH           = "./data/"
RAW_DATA_PATH       = DATA_PATH + "raw_data/"
PROCESSED_DATA_PATH = DATA_PATH + "processed_raw_data/"
COMPANY_ANALYSIS_PATH = DATA_PATH + "companies_analysis/"
MARKET_RESEARCH_PATH  = DATA_PATH + "market_research/"
DEEP_COMPERATIVE_PATH = DATA_PATH + "deep_comperative_analysis/"
BASIC_APP_STURCTURE_DIRS = [RAW_DATA_PATH, PROCESSED_DATA_PATH, COMPANY_ANALYSIS_PATH, MARKET_RESEARCH_PATH, DEEP_COMPERATIVE_PATH]


IB_DATA_PATH       = DATA_PATH + "ib_data/"
IB_FINANCIALS_PATH = DATA_PATH + IB_DATA_PATH + FINANCIALS

    # SICs
SIC_CODES_PATH = "./SICS/sic_codes.pkl"
SIC_DICIONARY_PATH = "./SICS/dictionary.pkl"

##################
SNAPSHOT_POSTFIX = "_snapshot.xml"


## IbTWS stuff ##
GET_FUNDUMENTALS = "fundumentals"
IBTWS_FUNCTIONS = [GET_FUNDUMENTALS]
#################

### PROCESSED XML FILES POSTFIX ###
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
