import logging as log
from copy import deepcopy

from hypernetworks.utils.HTTools import find_in

UP = 1
UP_AND_DOWN = 0
DOWN = -1


# TODO WIP
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


def get_path(hn, vertex, sb=None):
    if not sb:
        sb = hn.hypernetwork[vertex].B

    path = HsPath(hn.hypernetwork, vertex=vertex)

    if vertex in hn.hypernetwork:
        path.gen_path(hn.hypernetwork[vertex], sb)
    else:
        path.paths = None

    return path


def get_paths(hn, ignore_sb, *vertex_list):
    # Side-effects: changes temp.paths; new; existing
    paths = {}

    if ignore_sb:
        sb = None
    else:
        sb = hn.hypernetwork[vertex_list[0]].B

    for vtx in vertex_list:
        paths.update({vtx: get_path(hn, vtx, sb)})

    return paths


def get_underpath(hn, vertex, sb=None):
    if not sb:
        sb = hn.hypernetwork[vertex].B

    path = HsPath(hn.hypernetwork, vertex=vertex)

    if vertex in hn.hypernetwork:
        path.gen_underpath(hn.hypernetwork[vertex], sb)
    else:
        path.paths = None

    return path


# TODO Needs evaluating, may be able to replace with memberOf and contains.
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
    for step in path1:
        if step in path2:
            return step

    return None


def get_peaks(hn):
    res = []

    for name in hn.hypernetwork:
        hs = hn.hypernetwork[name]
        if hs.partOf == set():
            res.append(hs.vertex)

    return res


# TODO should be moved somewhere more generic.
def passbyval(func):
    def new(*args):
        cargs = [deepcopy(arg) for arg in args]
        return func(*cargs)
    return new


class HsPath:
    def __init__(self, hn, vertex="", paths=None):
        if paths is None:
            paths = []

        self._hn = hn
        self._vertex = vertex
        self._paths = paths[:]

    @property
    def vertex(self):
        return self._vertex

    @vertex.setter
    def vertex(self, value):
        self._vertex = value

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
                path_so_far = [vertex.vertex]
            else:
                path_so_far.append(vertex.vertex)

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

    def gen_underpath(self, vertex, sb):
        @passbyval
        def _gen_path(vertex, path_so_far=None, idx=0):
            if path_so_far is None:
                path_so_far = [vertex.vertex]
            else:
                path_so_far.append(vertex.vertex)

            if not (sb and len(sb.intersection(vertex.B)) == 0):
                if vertex.simplex == set() and idx == 0:
                    self._paths.append(path_so_far)
                    return 0, path_so_far

                for part in vertex.simplex:
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
