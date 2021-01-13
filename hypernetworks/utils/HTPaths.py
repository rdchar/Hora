import logging as log
from copy import deepcopy

import hypernetworks.core.Hypernetwork
from hypernetworks.core.Algebra import memberOf
from hypernetworks.utils.HTTools import find_in, passbyval


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

            if first:
                partOf = hn_partOf
                first = False
            else:
                if len(partOf & hn_partOf) > 0:
                    partOf = partOf & hn_partOf

                count -= 1

    return partOf, (num - count) / num


def get_path(hn, from_vertex, to_vertex="", ignore_sb=False, sb=None):
    if not ignore_sb and not sb:
        sb = hn.hypernetwork[from_vertex].B

    path = HsPath(hn.hypernetwork, vertex=from_vertex)

    if from_vertex in hn.hypernetwork:
        path.gen_path(from_vertex, to_vertex, sb)
    else:
        path.paths = []

    return path


def get_paths(hn, ignore_sb, *vertex_list):
    def _get_members():
        members = []

        for x in vertex_list:
            for y in vertex_list:
                if x != y:
                    if memberOf(hn, x, y):
                        members.append((x, y))
                    if memberOf(hn, y, x):
                        members.append((y, x))

        return members
    # End _get_members

    # Side-effects: changes temp.paths; new; existing
    paths = {}

    if ignore_sb:
        sb = None
    else:
        sb = hn.hypernetwork[vertex_list[0]].B

    if len(vertex_list) == 1:
        paths.update({vertex_list[0]: [[vertex_list[0]]]})

    elif len(vertex_list) > 1:
        members = _get_members()

        for from_vertex, to_vertex in members:
            new_path = []
            path = get_path(hn, from_vertex, to_vertex, ignore_sb, sb)

            if path:
                for p in path.paths:
                    for to_vertex in vertex_list:
                        if to_vertex != from_vertex and to_vertex in p:
                            new_path.append(path)
                            paths.update({from_vertex: new_path})

    return paths


def get_underpath(hn, vertex, ignore_sb=False, sb=None):
    if not ignore_sb and not sb:
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

    def gen_path(self, from_vertex, to_vertex="", sb=None):
        @passbyval
        def _gen_path(_vertex, path_so_far=None, idx=0):
            if path_so_far is None:
                path_so_far = [_vertex.vertex]
            else:
                path_so_far.append(_vertex.vertex)

            # If the specified vertex is found, or if the vertex has not been specified and the peak has been found
            if _vertex.vertex == to_vertex or (not to_vertex and len(_vertex.partOf) == 0):
                self._paths.append(path_so_far)
                idx += 1

            else:
                if sb and len(hypernetworks.core.Hypernetwork.intersection(_vertex.B)) == 0:
                    return

                for part in _vertex.partOf:
                    idx, result = _gen_path(self._hn[part], path_so_far, idx)

            return idx, path_so_far
        # End _gen_path

        _gen_path(self._hn[from_vertex])

        return self._paths

    def gen_underpath(self, vertex, sb):
        @passbyval
        def _gen_path(vertex, path_so_far=None, idx=0):
            if path_so_far is None:
                path_so_far = [vertex.vertex]
            else:
                path_so_far.append(vertex.vertex)

            if not (sb and len(hypernetworks.core.Hypernetwork.intersection(vertex.B)) == 0):
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
