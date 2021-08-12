import cfg

class proj_Series(cfg.pd.Series):
    @property
    def _constructor(self):
        return proj_Series

    @property
    def _constructor_expanddim(self):
        return proj_Series

    def _align_indexes(self, other):

        self_idxs  = "".join(self.index)
        other_idxs = "".join(self.index)

        other_c = other.copy()
        if ("-06-" in self_idxs or "-03-" in self_idxs or "-09-" in self_idxs):
            other_c.index = self.index

        else:
            self.index = other.index
        return other_c

    def _preoperators(self, other):
        self.fillna(0.0)
        other_c = other.copy().fillna(0.0)
        return other_c
    # OVERRIDES #

    def __add__(self, other):
        other_c = self._preoperators(other)
        if self.empty:
            return other_c
        elif other_c.empty:
            return self
        else:
            other_c = self._align_indexes(other_c)
            return super().__add__(other_c)

    def __sub__(self, other):
        other_c = self._preoperators(other)
        if self.empty:
            return other_c
        elif other_c.empty:
            return self
        else:
            other_c = self._align_indexes(other_c)
            return super().__sub__(other_c)
