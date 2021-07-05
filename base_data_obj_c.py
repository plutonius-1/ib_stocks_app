import cfg

_data_types =
    {

    }


class Base_data_obj_c:
    def __init__(self):
        self._data_type_description = None
        self._data                  = None
        self._last_updated          = None

    def set_data_type_descriptoin(self, data_type : str):
        self._data_type_description = _data_types[data_type]

    def set_data(self, data):
        self._data = data

    def set_last_updated(self, date : str):
        """
        @ param - data format is year-month-day
        """
        assert cfg.re_date_format.match(data), "{} is not in format {}".format(date ,cfg.RE_DATE_FORMAT)
        self._last_updated = date

    def __repr__(self):
        return "*** DATA OBJECT ***\n\tTYPE: {}\n\tLAST_UPDATED: {}".format(self._data_type_description,
                                                                            self._last_updated)
