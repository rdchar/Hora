class TrafficNotInHnError(Exception): pass
class TrafficDupInUnionError(Exception): pass


class Traffic:
    def __init__(self, hn):
        self._assoc_hn = hn
        self._traffic = {}  # key references the Hs and value is some app specific KISS value
        self._t = 0         # point in time

    @property
    def traffic(self):
        return self._traffic

    @traffic.setter
    def traffic(self, traffic):
        self._traffic = traffic

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, t):
        self._t = t

    def inc_t(self):
        self._t += 1

    def reset_t(self):
        self._t = 0

    @property
    def assoc_hn(self):
        return self._assoc_hn.name

    def add(self, key, value):
        if key in self._assoc_hn.hypernetwork:
            self._traffic.update({key: value})
        else:
            raise TrafficNotInHnError

    def update(self, key, value):
        # if key in self._traffic:
        self._traffic.update({key: value})
        # else:
        #     raise TrafficNotInHnError

    def __delitem__(self, key):
        del self._traffic[key]

    def union(self, traffic):
        intersection = set(self._traffic.keys()).intersection(traffic.keys())

        for i in intersection:
            if not self._traffic[i] == traffic[i]:
                raise TrafficDupInUnionError

        for key, value in traffic:
            self.add(key, value)

        # TODO ensure that the new Hn replaces the assoc_hn
        # self._assoc_hn = ?
