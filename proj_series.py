import cfg

class proj_Series(cfg.pd.Series):
    @property
    def _constructor(self):
        return SubclassedSeries

    @property
    def _constructor_expanddim(self):
        return SubclassedDataFrame

    def _align_indexes(self, other):

        self_idxs  = "".join(self.index)
        other_idxs = "".join(self.index)

        if ("-06" in self_idxs or "-03-" in self_idxs or "-09-" in self_idxs):
            other.index = self.index
        else:
            self.index = other.index
        return other

    def __add__(self, other):
        other = self._align_indexes(other)
        return super().__add__(other)
    def __sub__(self, other):
        other = self._align_indexes(other)
        return super().__sub__(other)
