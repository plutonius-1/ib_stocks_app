from datetime import datetime
import threading
import cfg
import proj_utils
from cfg import pd

AVAIL = "AVAIL"
OUT   = "OUT"
REQ_ID_STATUSES = {"AVAIL" : "availabe",
                   "OUT"   : "out"}

class Req_id_c:
    def __init__(self):
        self.id     = None
        self.status = REQ_ID_STATUSES[AVAIL]

    def set_id(self, _id):
        self.id = _id

class Req_id_handler_c:
    def __init__(self):
        self.requsts_file = self.get_local_requests_file()

    def get_local_requests_file(self):
        if (not cfg.os.path.exists(cfg.IB_REQUEST_HISTORY_PATH)):
            return cfg.DEFAULT_IB_REQ_HISTORY_DICT
        else:
            return pd.read_pickle(cfg.IB_REQUEST_HISTORY_PATH)
