"""
Base class for XML readers
"""

import xml.etree.ElementTree as ET
import pandas as pd
import pickle
import cfg

class baseXMLReader_c:
    def __init__(self):
        self._xml_path = None
        self._xml_master = None


    def get_xml_master(self):
        return self._xml_master

    def set_xml_path(self, new_xml_path):
        assert cfg.os.path.exists(new_xml_path)
        self._xml_path = new_xml_path

    def set_xml_master(self, new_xml_path)
        self.set_xml_path(new_xml_path)
        tree = ET.parse(self._xml_path)
        root = tree.getroot()
        self._xml_master = root



