import IbTWS_c



class Api_Handler:
    def __init__(self,
                 host : str,
                 port : str,
                 clientId : int
                 ):

        self.tws_api_c = IbTWS_c.IbTws(host = host, port = port, clientId = clientId)


    #####
