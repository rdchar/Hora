
class Types:
    class _type:
        def __init__(self, values):
            self._mutable = values[0]
            self._values = () if len(values) == 1 else values[1]

        @property
        def mutable(self):
            return self._mutable

        @property
        def values(self):
            return self._values

        def __iadd__(self, other):

            self._values.update(other)

        def __contains__(self, item):
            return item in self._values

        @mutable.setter
        def mutable(self, m):
            # TODO log cannot reset mutable
            pass

    def __init__(self):
        self._types = {}

    @property
    def types(self):
        return list(self._types.keys())

    def __setitem__(self, key, item):
        self._types[key] = self._type(item)

    def __getitem__(self, item):
        return self._types[item]

    def __iadd__(self, other):
        print("HELLO 1")
        self.types += other

    @types.setter
    def types(self, value):
        print(value)
        self._types = value
