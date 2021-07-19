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

        self.current_requests_ids = 100
        self.avail_requests = [i for i in range(self.current_requests_ids)]
        self.outgoing_reqs = {}
        self.waiting_for_response = False
        self.time = datetime.now()
        self.error_ids = []
        self.reqs_history = self.get_local_requests_file()
        # pacing stuff #
        self.reqs_counter = cfg.IB_MAX_REQUESTS_PER_10_MIN
        self._halt_due_to_pacing = False
        pacing_counter_thread = threading.Thread(target = self._reached_pacing_max)
        pacing_counter_thread.start()

    def register_outgoing_req(self, historical):

        while self._halt_due_to_pacing:
            cfg.time.sleep(60)
            proj_utils.print_warning_msg(str(__file__) + ": Halting new requests to avoid pacing issues")

        if (len(self.avail_requests) == 0):

            new_avail_requests = [i for i in range(self.current_requests_ids, self.current_requests_ids *2)]

            # new_avail_requests = new_avail_requests[self.current_requests_ids:]

            self.current_requests_ids *= 2
            self.avail_requests =  new_avail_requests


        outgoind_id = self.avail_requests.pop()
        outgoind_id = int(outgoind_id)
        self.outgoing_reqs.update({outgoind_id : OUT})
        self.waiting_for_response = True
        self.reqs_counter -= 1
        if (self.reqs_counter == 1):
            self._halt_due_to_pacing = True
        return outgoind_id

    def response_id(self, _id):
        _id = int(_id)
        # del self.outgoing_reqs[_id]
        # if (len(self.outgoing_reqs) == 0):
            # self.waiting_for_response = False

        self.del_from_out_going_reqs(_id)
        self.avail_requests.append(_id)

    def del_from_out_going_reqs(self ,_id):
        _id = int(_id)
        del self.outgoing_reqs[_id]
        if (len(self.outgoing_reqs) == 0):
            self.waiting_for_response = False

    def get_num_outgoing_reqs(self):
        return len(self.outgoing_reqs)

    def add_to_error_ids(self, _id):
        _id = int(_id)
        self.error_ids.append(_id)

    # def _reached_10_min_max_reqs(self):
    def _reached_pacing_max(self):
        while True:
            minuets = 10
            while minuets > 0:
                if (self.reqs_counter == 1):
                    self._halt_due_to_pacing = True
                else:
                    self._halt_due_to_pacing = False
                cfg.time.sleep(60)
                minuets -= 1
            minuets = 10
            self.reqs_counter = cfg.IB_MAX_REQUESTS_PER_10_MIN
            self._halt_due_to_pacing = False

    def get_local_requests_file(self):
        if (not cfg.os.path.exists(cfg.IB_REQUEST_HISTORY_PATH)):
            return cfg.DEFAULT_IB_REQ_HISTORY_DICT
        else:
            return pd.read_pickle(cfg.IB_REQUEST_HISTORY_PATH)



