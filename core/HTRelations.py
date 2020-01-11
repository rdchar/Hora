

class Relations:
    class _relation:
        def __init__(self, struct):
            self._struct = struct

        @property
        def struct(self):
            return self._struct

        @struct.setter
        def struct(self, value):
            self._struct = value

        def __str__(self):
            return str(self._struct)

    def __init__(self):
        self._relations = {}

    @property
    def relations(self):
        return self._relations

    def __getitem__(self, item):
        if item in self._relations:
            return self._relations[item]

        # TODO log if doesn't exists
        return []

    def __setitem__(self, key, value):
        if not self._relations.get(key) and value:
            self._relations.update({key: value})

    def __str__(self):
        res = ""
        for k, v in self.relations.items():
            res += k + " = " + str(v) + "\n"
        return res
