import os
import cfg
import xml.etree.ElementTree as ET

def get_and_varify_page(self,
                        third_party_name : str,
                        ticker : str,
                        link : str,
                        filter_function = None):

    req = requests.get(self.THIRD_PARTYS_FINANCIALS_LINKS[third_party_name].format(ticker))
    if not req.ok or "table" not in req.text:
        return None
    else:
        filter_func = filter_functions[third_party_name]
        filterd_results = list(filter(filter_func, pd.read_html(req.content)))
        if (len(filterd_results) == 0):
            return None
        merged_df = pd.concat(filterd_results)
    return merged_df

# for third_party_name in self.VALID_THIRD_PARTIES:
    # profile_df = get_and_varify_page(self, third_party_name, self.ticker)
    # self.profiles.update({third_party_name : profile_df})
# return

def check_dir_exists(path : str):
    if (os.path.exists(path) is False):
        os.mkdir(path)
    return True

def get_xml_elem(xml_file_path : str,
                 dir_path_in_file : str):
    assert cfg.os.path.exists(xml_file_path), "file {} does not exists".format(xml_file_path)
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    elem = root.find(dir_path_in_file)
    return elem

