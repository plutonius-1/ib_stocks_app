import xml.etree.ElementTree as ET
import pandas as pd
import pickle
import cfg
import proj_utils

class snapshotXmlReader_c:
    def __init__(self):
        self.ticker = None
        self.snapshot_path = None
        self.INDUSTRY_INFO_DIR_PATH = "./peerInfo/IndustryInfo"
        self.RATIOS_INFO_DIR_PATH   = "./Ratios"

    ### GETS ###
    def get_sics(self):
        assert self.ticker != None
        industry_info = proj_utils.get_xml_elem(xml_file_path = self.snapshot_path,
                                                dir_path_in_file = self.INDUSTRY_INFO_DIR_PATH)
        sics = {}
        for ind in industry_info:
            if ind.attrib["type"] == "SIC":
                sics.update({ind.attrib["code"] : ind.text})
        if (len(sics.keys()) == 0):
            print("*** Warning: found 0 SICS for {} ***".format(self.ticker))
        return sics

    def get_ratios(self):
        """
        Returns a dict:
        {"last date":
            "{group : ratio_obj},
             {group2 : ratio_obj}"
        }
        """
        assert self.ticker != None
        ratios_dict = {}

        ratios = proj_utils.get_xml_elem(self.snapshot_path,
                                         self.RATIOS_INFO_DIR_PATH)
        last_available_date = ratios.attrib["LatestAvailableDate"]

        for group in ratios:
            group_name = group.attrib["ID"]
            group_dict = {group_name : {}}

            for ratio in group:
                field_name = ratio.attrib["FieldName"]
                value      = ratio.text
                d = {field_name : value}
                group_dict[group_name].update(d)

            ratios_dict.update(group_dict)
        return ratios_dict

    ### SETS ###
    def set_ticker(self, ticker):
        self.ticker = ticker
        self.snapshot_path = cfg.IB_FINANCIALS_PATH + self.ticker + "_snapshot.xml"


c = snapshotXmlReader_c()
c.set_ticker("MMM")
print(c.get_sics())
print(c.get_ratios())
