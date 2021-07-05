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
    splt = path.split("/") # [".', "abc" , "de"]
    idx = 1
    if (os.path.exists(path)):
        return True

    while (idx != len(splt) + 1):
        temp_path = "/".join(splt[:idx])
        if (os.path.exists(temp_path) is False):
            os.mkdir(temp_path)
        idx += 1

    return True

def check_file_exist(path : str):
    if os.path.exists(path): return True
    else: return False

def get_xml_elem(xml_file_path : str,
                 dir_path_in_file : str):
    # assert cfg.os.path.exists(xml_file_path), "file {} does not exists".format(xml_file_path)
    if not cfg.os.path.exists(xml_file_path):
        print_warning_msg("WARNING: file {} does not exists - returning None".format(xml_file_path))
        return None
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    elem = root.find(dir_path_in_file)
    return elem

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_warning_msg(msg : str):
    print(bcolors.WARNING + msg + bcolors.ENDC)

def print_sleep_msg(timeout = 0, msg = ""):
    while (timeout > 0):
        print(bcolors.OKGREEN + msg + ": sleeping for {}".format(timeout) + bcolors.ENDC)
        cfg.time.sleep(1)
        timeout -= 1
    return None

def _finditem(obj, key):
    if key in obj: return obj[key]
    for k, v in obj.items():
        if isinstance(v,dict):
            item = _finditem(v, key)
            if item is not None:
                return item

def get_date():
    local_time_obj = cfg.time.localtime()
    y = local_time_obj.tm_year
    m = local_time_obj.tm_mon
    d = local_time_obj.tm_mday

    return str(y+"-"+m+"-"+d)
