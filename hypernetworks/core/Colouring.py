class ColouringNotInHnError(Exception): pass
class ColouringDupInUnionError(Exception): pass


class Colouring:
    def __init__(self, hn):
        self._assoc_hn = hn
        self._colouring = {}  # key references the Hs and value is some app specific structure

    @property
    def colouring(self):
        return self._colouring

    @colouring.setter
    def colouring(self, colouring):
        self._colouring = colouring

    @property
    def assoc_hn(self):
        return self._assoc_hn.name

    def add(self, key, value):
        if key in self._assoc_hn.hypernetwork:
            self._colouring.update({key: value})
        else:
            raise ColouringNotInHnError

    def update(self, key, value):
        if key in self._colouring:
            self._colouring.update({key: value})
        else:
            raise ColouringNotInHnError

    def load(self, fname="", data=None):
        # TODO should be able to provide the data or a file from which to load the data
        def _load_from_file():
            pass

        pass

    def __delitem__(self, key):
        del self._colouring[key]

    def union(self, colouring):
        # TODO implement this properly.  The colouring blocks could be complex structures, so hard to compare
        # TODO ensure that the new Hn replaces the assoc_hn
        # intersection = set(self._colouring.keys()).intersection(colouring.keys())
        #
        # for i in intersection:
        #     if not self._colouring[i] == colouring[i]:
        #         raise ColouringDupInUnionError

        for key, value in colouring:
            self.add(key, value)
