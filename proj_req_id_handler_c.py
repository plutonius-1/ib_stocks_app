
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



    def register_outgoing_req(self):

        if (len(self.avail_requests) == 0):

            new_avail_requests = [i for i in range(self.current_requests_ids *2)]

            new_avail_requests = new_avail_requests[self.current_requests_ids:]

            self.current_requests_ids *= 2
            self.avail_requests = new_avail_requests


        outgoind_id = self.avail_requests.pop()
        self.outgoing_reqs.update({outgoind_id : OUT})
        self.waiting_for_response = True
        return outgoind_id

    def response_id(self, _id):
        del self.outgoing_reqs[_id]
        self.avail_requests.append(_id)

    # def _initilize_req_dict(self, init_number_of_ids):
        # for i in range(init_number_of_ids):
            # req = Req_id_c(i)
            # self.requests.update({req : req.status})


