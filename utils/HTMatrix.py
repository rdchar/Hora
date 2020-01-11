import logging as log

import numpy as np

from core.HTErrors import HnSearchError, HnVertexNoFound
from core.Hypersimplex import ALPHA, BETA, VERTEX


# TODO need to manage the decorators.


def to_matrix(Hn, vertex="", R=""):
    class visit:
        ed = {}

    def _parse_hn_to_matrix(_hs):
        def _get_line(__current):
            _res = []
            _line = []
            _finished = True

            if __current.hstype == ALPHA:
                for _vertex in __current.simplex:
                    _prev_fin = _finished
                    (_line, _finished) = _get_line(Hn.hypernetwork[_vertex])
                    _res.extend(_line)

                    # Ensure that if a prev branch returned False then the setting is retained
                    _finished = _prev_fin if _finished else _finished

            elif __current.hstype == BETA:
                for _vertex in __current.simplex:
                    if __current.vertex not in visit.ed or _vertex not in visit.ed[__current.vertex]:
                        (_line, _finished) = _get_line(Hn.hypernetwork[_vertex])
                        _res.extend(_line)

                        if _finished:
                            if __current.vertex not in visit.ed:
                                visit.ed.update({__current.vertex: [_vertex]})  # Add
                            else:
                                visit.ed[__current.vertex].append(_vertex)  # Update

                        if __current.vertex in visit.ed:
                            # TODO changed __current._vertex to __current.vertex
                            _finished = isinstance(__current.vertex, list) \
                                        and len(visit.ed[__current.vertex]) == len(__current.simplex)
                        else:
                            _finished = False

                        break

            elif __current.hstype == VERTEX:
                _res.append(__current.vertex)

            else:
                log.error("_parse_hn_to_matrix: Unknown Hs type!")
                raise HnSearchError

            return _res, _finished
        # End _get_line

        res = []
        max_len = 0

        while True:
            (line, finished) = _get_line(_hs)

            if line not in res:
                if res:
                    for r in res:
                        if not set(line).issubset(set(r)):
                            res.append(line)
                            max_len = max_len if len(line) < max_len else len(line)
                            break

                else:
                    max_len = len(line)
                    res.append(line)

            if finished:
                break

        for i, line in enumerate(res):
            if len(line) != max_len:
                del res[i]

        return res
    # End _parse_hn_to_matrix

    M = []

    if R:
        vertices = Hn.search(R=R)
    elif vertex:
        vertices = Hn.search(vertex=vertex)
    else:
        vertices = Hn.hypernetwork.keys()

    for vert in vertices:
        m = _parse_hn_to_matrix(Hn.hypernetwork[vert])

        if len(m) == 1 and isinstance(m[0], list):
            m = m[0]

        M.append(m)

    if len(M) == 1:
        return M[0]

    return M


def from_matrix(Hn, M, vertex="", R="", replace=True):
    """
    :type M: numpy.ndarray
    """
    # res = vertex + "=" if vertex else ""
    def _from_matrix(_M):
        res = []
        if _M.size > 1:
            (lhs, mid, rhs) = _outside_in(_M)
            mid = _split_into_unique(mid.T)
            outer = []

            if len(lhs) > 0 or len(rhs) > 0:
                # VERTICES
                for l in lhs:
                    outer.append(l)

            if len(mid) == 1:
                # BETA
                for m in mid[0]:
                    temp = []
                    for v in m:
                        if isinstance(v, str):
                            temp.append(v)
                        else:
                            temp.append([_from_matrix(m)])

                    if temp:
                        outer.append([{"BETA": np.unique(temp).tolist()}])

            elif len(mid) > 1:
                # BETA
                temp = []
                for m in mid:
                    if len(m) == 1:
                        if isinstance(m[0], str):
                            temp.append(m[0])
                        else:
                            temp.append([x for x in m[0]])
                    else:
                        temp.append([_from_matrix(np.array(m).T)])

                if temp:
                    outer.append([{"BETA": temp}])

            if len(lhs) > 0 or len(rhs) > 0:
                # VERTICES
                for r in rhs:
                    outer.append(r)

                res = {"ALPHA": outer}

            else:
                res = [{"BETA": outer}]

        return res
    # End _from_matrix

    temp = [_from_matrix(np.array(M).T)]

    if R:
        temp.append({"R": R})

    if replace:
        try:
            Hn.delete(vertex=vertex, R=R)

        except HnVertexNoFound:
            print("Not found: " + R + " " + vertex)
            return

    if vertex:
        temp = [{"VAL": vertex}, temp[0] if isinstance(temp[0], list) else temp]

    Hn.parse(temp)


def matrix_to_string(M, vertex="", R=""):
    """
    :type M: numpy.ndarray
    """

    res = vertex + "=" if vertex else ""

    if M.size > 1:
        (lhs, mid, rhs) = _outside_in(M)
        mid = _split_into_unique(mid.T)

        if len(lhs) > 0 or len(rhs) > 0:
            res += "<" + ",".join(lhs) + ("," if len(lhs) > 0 else "")

        if len(mid) > 0:
            if len(mid) == 1:
                res += "<"

                for m in mid[0]:
                    comma = False
                    res += "{"
                    for v in m:
                        if isinstance(v, str):
                            if comma:
                                res += ','
                            else:
                                comma = True
                            res += v
                        else:
                            res += str(matrix_to_string(m))
                    res += "}"

                res += ">"

            else:
                res += "{"

                comma = False
                for m in mid:
                    if len(m) == 1:
                        if isinstance(m[0], str):
                            if comma:
                                res += ","
                            else:
                                comma = True
                            res += str(m[0])
                        else:
                            res += "<" + ",".join(m[0]) + ">"
                    else:
                        res += str(matrix_to_string(np.array(m).T))

                res += "}"

        if len(lhs) > 0 or len(rhs) > 0:
            res += ("," if len(rhs) > 0 else "") + ",".join(rhs) + ">"

        # A cheat to ensure correct formatting!
        res = res.replace("><", ">,<")
        res = res.replace("}{", "},{")
        res = res.replace(",>", ("; R_" + R if R else "") + ">")

    return res


def _reverse(m):
    return [list(reversed(e)) for e in m]


def _remove_outer_brackets(m):
    while len(m) == 1:
        if isinstance(m[0], list):
            m = m[0]

        else:
            break

    return m


def _get_unique(x):
    res = []
    i = 0

    if isinstance(x, str):
        res = [x]

    else:
        for y in x:  # y can be a list or str
            if y not in res:
                res.append(y)
                i += 1

    return _remove_outer_brackets(res)


def _test_for_unique(m):
    for x in m:
        unique = _get_unique(x)

        for u in unique:
            if x.count(u) % 2 != 0:
                return False

    return True


def _outside_in(_M):
    def _left_right(__M):
        counter = 0
        common = []
        remainder = []

        for f in __M:
            (_unique, _count) = np.unique(f, return_counts=True)
            if len(_unique) == 1 and len(f) > 1:
                common.extend(_unique)
                counter += 1
            else:
                remainder = __M[counter:]
                break

        return np.array(common), np.array(remainder)

    # END left_right

    _mid = np.array([])
    _lhs = np.array([])
    _rhs = np.array([])

    (_lhs, _mid) = _left_right(_M)
    (_rhs, _mid) = _left_right(np.flip(_mid, 0))
    _mid = np.flip(_mid, 0)

    return _lhs, _mid, _rhs


def _split_into_unique(_M):
    def _sub_matrix(__sm, __M):
        __sm = np.array(__sm)
        __M = np.array(__M)

        if __sm.size > __M.size:
            return False

        unique = np.unique(np.isin(__sm, __M))

        return unique.size == 1 and unique[0]
    # END sub_matrix

    def _split(__M):
        __res = {}

        for __m in __M.tolist():
            if __m:
                first = __m[0]
                if first in __res:
                    __res[first].append(__m)
                else:
                    __res.update({first: [__m]})

                last = __m[len(__m) - 1]
                if last in __res:
                    __res[last].append(__m)
                else:
                    __res.update({last: [__m]})

        return __res.values()
    # END split

    if len(_M.T.tolist()) == 1:
        return _M

    _res = []
    splitM = list(_split(_M))

    # Remove contained in
    for _m in splitM[:]:
        for _n in splitM[:]:
            if _n != _m and _sub_matrix(_n, _m):
                splitM.remove(_n)

    # Dedup
    for s in splitM:
        if s not in _res:
            _res.append(s)

    # TODO: BEGIN FUDGE!
    # Dedup to force an ALPHA
    #   If the count of each vertex is equal for each column in the matrix,
    #   then it should be an Alpha.
    alpha = False
    for r in np.array(_res).T:
        if isinstance(r, list):
            break

        (x, y) = r.shape
        r = r.reshape((1, x * y))
        vals = np.array(np.unique(r[0], return_counts=True))
        count = np.unique(vals[1])

        if len(count) != 1:
            break
        # The number of elements in the original matrix should be
        # = to the count of the vertex in the flattened matrix.
        alpha = int(list(count)[0]) == y

        if not alpha:
            break

    if alpha:
        _temp = []
        oldlen = -1

        for r1 in np.array(_res).T:
            for r2 in r1:
                x = np.unique(r2).tolist()

                if _temp:
                    for t in _temp:
                        if oldlen == -1 or oldlen == len(t):
                            oldlen = len(t)

                            if x not in _temp:
                                _temp.append(x)

                else:
                    _temp.append(x)

        _res = [_temp]
        # TODO: END FUDGE!

    return np.array(_res)