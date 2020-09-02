import collections
import logging as log

from hypernetworks.core import HS_TYPE, NONE, VERTEX
from hypernetworks.utils import find_in

UP = 1
UP_AND_DOWN = 0
DOWN = -1


def best_fit(hn, search_hn, top):
    """
    temp = []
    for t in search_hn[top].simplex:
        temp.append("<" + ", ".join(search_hn[t].simplex) + ">")
    print("<" + str(", ".join(temp)) + ">")
    """
    partOf = set()
    first = True
    count = len(search_hn.hypernetwork[top].simplex)
    num = count

    for v in search_hn.hypernetwork[top].simplex:
        hstype = search_hn.hypernetwork[v].hstype
        simplex = search_hn.hypernetwork[v].simplex
        search = hn.search(hstype=hstype, simplex=simplex)

        for h in search:
            hn_partOf = hn.hypernetwork[h].partOf
            # print("\t" + h + ": " + str(hn.hypernetwork[h].simplex))

            if first:
                partOf = hn_partOf
                first = False
            else:
                if len(partOf & hn_partOf) > 0:
                    partOf = partOf & hn_partOf

                count -= 1
            # print("\t\t: " + str(partOf))

    return partOf, (num - count) / num


def get_paths(hn, simplex):
    # Side-effects: changes temp.paths; new; existing
    paths = collections.OrderedDict()
    new = []
    existing = []

    for idx, vtx in enumerate(simplex):
        path = HsPath(hn.hypernetwork, pos=idx, vertex=vtx)

        if vtx in hn.hypernetwork:
            path.gen_path(hn.hypernetwork[vtx])
        else:
            path.path = None

        paths.update({tuple((idx, vtx)): path})

    for idx, path in paths.items():
        if path.path:
            existing.append(tuple((path.pos, path.vertex)))
        else:
            new.append(tuple((path.pos, path.vertex)))

    return paths


def in_path(hn, start, val, dir=UP_AND_DOWN):
    def _in_path(_start, _dir):
        _res = False

        if _start in hn.hypernetwork:
            partOf = hn.hypernetwork[_start].partOf
            simplex = hn.hypernetwork[_start].simplex

            for vertex in (partOf if _dir == UP else simplex):
                if find_in(val, partOf) or find_in(val, simplex):
                    _res = True

                else:
                    if partOf == {}:
                        _res = False
                    else:
                        _res = _in_path(vertex, _dir)

                if _res:
                    break
        else:
            _res = False

        return _res
    # End _in_path

    res = False

    if dir in [UP, UP_AND_DOWN]:
        res = _in_path(start, UP)

    if dir in [DOWN, UP_AND_DOWN] and not res:
        res = _in_path(start, DOWN)

    return res


def find_head(path1, path2):
    for step in path1.path:
        if step in path2.path:
            return step

    return None


def get_peaks(hn):
    res = []

    for hs in hn.values():
        if hs.partOf == set():
            res.append(hs.vertex)

    return res


class hsPathElem:
    def __init__(self, pathID=0, vertex="", hstype=NONE):
        self._pathID = pathID
        self._vertex = vertex
        self._hstype = hstype

    @property
    def pathID(self):
        return self._pathID

    @property
    def vertex(self):
        return self._vertex

    @property
    def hstype(self):
        return self._hstype

    def __eq__(self, other):
        return self._vertex == other.vertex and self._hstype == other.hstype

    def __str__(self):
        return "<" + str(self.pathID) + "; " + self.vertex + "; " + str(HS_TYPE[self.hstype + 1]) + ">"


class HsPath:
    def __init__(self, hn, vertex="", pos=0, path=None):
        if path is None:
            path = []

        self._hn = hn
        self._vertex = vertex
        self._pos = pos
        self._path = path[:]

    @property
    def vertex(self):
        return self._vertex

    @vertex.setter
    def vertex(self, value):
        self._vertex = value

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        self._pos = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    def __len__(self):
        return len(self._path)

    def __getitem__(self, item):
        return self._path[item]

    def __setitem__(self, key, value):
        self._path[key] = value

    def __contains__(self, item):
        log.debug("ITEM: " + str(item))
        return item in self._path

    def gen_path(self, vertex, old_idx=0):
        if vertex:
            if vertex.hstype != VERTEX:
                self._path.append(hsPathElem(old_idx, vertex.vertex, vertex.hstype))

            for idx, partOf in enumerate(vertex.partOf):
                if idx > old_idx:
                    old_idx = idx

                if not partOf:
                    break
                else:
                    self.gen_path(self._hn[partOf], old_idx)

        return self._path

    def __str__(self):
        res = ""
        first = True

        if self._path:
            for path in self._path:
                if first:
                    res += str(path)
                    first = False
                else:
                    res += " -> " + str(path)
        else:
            res = str(self.vertex) + " ... none"

        return res
