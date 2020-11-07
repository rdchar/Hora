import collections
import logging as log
from copy import deepcopy

from hypernetworks.core.Hypersimplex import HS_TYPE, VERTEX, NONE
from hypernetworks.utils.HTTools import find_in

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

    sb = hn.hypernetwork[simplex[0]].B

    for idx, vtx in enumerate(simplex):
        path = HsPath(hn.hypernetwork, pos=idx, vertex=vtx)

        if vtx in hn.hypernetwork:
            path.gen_path(hn.hypernetwork[vtx], sb)
        else:
            path.paths = None

        paths.update({tuple((idx, vtx)): path})

    for idx, path in paths.items():
        if path.paths:
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
    for step in path1.paths:
        if step in path2.paths:
            return step

    return None


def get_peaks(hn):
    res = []

    for hs in hn.values():
        if hs.partOf == set():
            res.append(hs.vertex)

    return res


def passbyval(func):
    def new(*args):
        cargs = [deepcopy(arg) for arg in args]
        return func(*cargs)
    return new


class hsPathElem:
    def __init__(self, vertex="", hstype=NONE):
        self._vertex = vertex
        self._hstype = hstype

    @property
    def vertex(self):
        return self._vertex

    @property
    def hstype(self):
        return self._hstype

    def __eq__(self, other):
        return self._vertex == other.vertex and self._hstype == other.hstype

    def __str__(self):
        return "(" + self.vertex + ", " + str(HS_TYPE[self.hstype + 1]) + ")"


class HsPath:
    def __init__(self, hn, vertex="", pos=0, paths=None):
        if paths is None:
            paths = []

        self._hn = hn
        self._vertex = vertex
        self._pos = pos
        self._paths = paths[:]

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
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, value):
        self._paths = value

    def __len__(self):
        return len(self._paths)

    def __getitem__(self, item):
        return self._paths[item]

    def __setitem__(self, key, value):
        self._paths[key] = value

    def __contains__(self, item):
        log.debug("ITEM: " + str(item))
        return item in self._paths

    def gen_path(self, vertex, sb):
        @passbyval
        def _gen_path(vertex, path_so_far=None, idx=0):
            if path_so_far is None:
                path_so_far = [hsPathElem(vertex.vertex, vertex.hstype)]
            else:
                path_so_far.append(hsPathElem(vertex.vertex, vertex.hstype))

            if not (sb and len(sb.intersection(vertex.B)) == 0):
                if vertex.partOf == set() and idx == 0:
                    self._paths.append(path_so_far)
                    return 0, path_so_far

                for part in vertex.partOf:
                    old_idx = idx
                    idx, result = _gen_path(self._hn[part], path_so_far, idx)

                    if old_idx == idx:
                        self._paths.append(result)
                        idx += 1

            return idx, path_so_far
        # End _gen_path

        _gen_path(vertex)

        return self._paths

    def __str__(self):
        res = ""

        if self._paths:
            for i, path in enumerate(self._paths):
                res += str(i) + " => "
                res += "->".join([str(y) for y in path])
                res += "\n"
        else:
            res = str(self.vertex) + " ... none"

        return res
