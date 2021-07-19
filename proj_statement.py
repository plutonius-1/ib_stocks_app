import cfg

class Statement:
    def __init__(self):
        self._name = None
        self._raw_data = None


    def set_name(self, name : str):
        assert name in cfg.STATEMENTS_NAMES
        self._name = name

    def set_raw_data(self, raw_data : dict)
        self._raw_data = raw_data
