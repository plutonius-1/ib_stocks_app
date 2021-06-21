import xml.etree.ElementTree as ET
import requests
import os
import pandas as pd

### GENERAL KEYWORDS ###

FINANCIALS = "financials"

### PATHS ###

IB_FINANCIALS_PATH = "./ib_data/financials/"

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
