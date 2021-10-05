import cfg
import proj_utils
from cfg import np



class Base_data_obj_c:
    def __init__(self):
        self._name                  = None
        self._data_type_description = None
        self._data                  = None
        self._processed_data        = None
        self._frequancy             = None
        self._last_updated          = self.set_last_updated() # update date when created



    ## Gets ##
    def get_name(self):
        return self._name

    def get_data(self):
        return self._data

    def get_processed_data(self):
        return self._processed_data

    def get_processed_data_type(self):
        return type(self._processed_data)

    def get_frequancy(self):
        return self._frequancy

    def get_last_updated(self):
        return self._last_updated


    ## Sets ##
    def set_data_type_descriptoin(self, data_type : str):
        # self._data_type_description = _data_types[data_type]
        return None

    def set_frequancy(self, freq):
        assert freq is cfg.Q or freq is cfg.K
        self._frequancy = freq

    def set_name(self, name : str):
        self._name = name

    def set_data(self, data):
        # assert type(data) == dict
        self._data = data
        return None

    def set_last_updated(self, date = None):
        if (date is None):
            return proj_utils.get_date()
        else:
            return date

    def set_processed_data(self, processed_data):
        self._processed_data = processed_data
        return None

    ## Overrides ##
    def __repr__(self):
        return "*** DATA OBJECT ***\n\tTYPE: {}\n\tLAST_UPDATED: {}".format(self._data_type_description,
                                                                            self._last_updated)
