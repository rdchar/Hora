import re

from hypernetworks.utils import condense_all_specials, remove_special

"""
from core.HTConfig import hs_replace_same_vertex
"""
from hypernetworks.core import HnInsertError, HnUnknownHsType, HnVertexNoFound
from hypernetworks.core import Relations
from hypernetworks.core import Types
from hypernetworks.core import Hypersimplex, NONE, VERTEX, ALPHA, BETA, str_to_hstype
import logging as log

"""
from utils.HTMatrix import to_matrix, from_matrix
"""

# TODO needs more validation when adding Hs.
#      We get a mess when mixing R naming and assignment names across Hs's.
from hypernetworks.utils import get_peaks

UP = 1
DOWN = -1


class Hypernetwork:
    _counter = 0

    def __init__(self, name="Unnamed"):
        self._hypernetwork = dict()
        self._name = name
        self._types = Types()
        self._relations = Relations()
        # self._counter = 0

    @property
    def counter(self):
        return self._counter

    @property
    def name(self):
        return self._name

    @property
    def hypernetwork(self):
        return self._hypernetwork

    @property
    def relations(self):
        return self._relations

    def load_hs(self, hs):
        self._hypernetwork.update({hs.vertex: hs})

    def add(self, vertex, hstype=NONE, simplex=None, R="", t=-1, A=None, N="", psi="", partOf=None):
        if vertex in self._hypernetwork:
            # Update an existing node
            temp = self._hypernetwork[vertex]

            if temp.hstype not in [NONE, VERTEX]:
                hstype = temp.hstype

            if temp.simplex and not simplex:
                simplex = temp.simplex[:]

            if temp.R == "" and R == "":
                R = temp.R

            if temp.A and A:
                A = temp.A.copy()

            if temp.N != "" and N == "":
                N = temp.N

            if temp.psi != "" and psi == "":
                psi = temp.psi

            if temp.partOf and not partOf:
                partOf = temp.partOf.copy()

            temp.update(hstype=hstype, simplex=simplex, R=R, t=t, A=A, N=N, psi=psi, partOf=partOf)
            self._hypernetwork[vertex] = temp

        else:
            # Create a new node
            hs = Hypersimplex(self, vertex, hstype=hstype, simplex=simplex, R=R, t=t, A=A, N=N, psi=psi, partOf=partOf)
            self._hypernetwork.update({vertex: hs})

        if R:
            self._relations[R] = None

    def add_hs(self, vertex="", hs=None):
        if vertex:
            vertex = hs.vertex

        self.insert(vertex, hstype=hs.hstype, simplex=hs.simplex, R=hs.R, t=hs.t, A=hs.A, N=hs.N, psi=hs.psi)

    def delete(self, vertex="", R=""):
        def _delete(_vertex, _parent=""):
            if _parent in self._hypernetwork[_vertex].partOf:
                self._hypernetwork[_vertex].partOf.remove(_parent)

            for _vert in self._hypernetwork[_vertex].simplex:
                if len(self._hypernetwork[_vertex].partOf) == 0:
                    _delete(_vert, _vertex)

            # Removes all instances of the vertex.
            for _whole in self._hypernetwork[_vertex].partOf:
                for _part in self._hypernetwork[_whole].simplex:
                    if _part == _vertex:
                        self._hypernetwork[_whole].simplex.remove(_part)

            if len(self._hypernetwork[_vertex].partOf) == 0:
                del self._hypernetwork[_vertex]

        # TODO may need more work
        if R:
            vertices = self.search(R=R)
            for vert in vertices:
                _delete(_vertex=vert)

        elif vertex and vertex in self._hypernetwork:
            _delete(_vertex=vertex)

        else:
            raise HnVertexNoFound

    def insert(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, A=None, N="", psi="", partOf=None):
        def _update_N(_N, _direction=UP):
            res = ""
            l = len(_N)
            if _N:
                if _direction == UP:
                    if l == 1:
                        res = "N+1"
                    else:
                        level = int(_N[:l - 1]) + 1
                        res[:l] = str(level)

                elif _direction == DOWN:
                    if l == 1 or _N[:l - 1] == 1:
                        res = "N"
                    elif l > 2:
                        level = int(_N[:l - 1]) - 1
                        res[:l] = str(level)

            return res
        # End _update_N

        if simplex is None:
            simplex = []

        if partOf is None:
            partOf = set()

        # TODO is this the right solution?  Or should it we use the matrix method.
        if vertex in self.hypernetwork:
            if self.hypernetwork[vertex].hstype == BETA and self.hypernetwork[vertex].simplex != simplex:
                # Add to BETA
                if hstype == BETA:
                    self.hypernetwork[vertex].simplex = \
                        list(sorted(set(self.hypernetwork[vertex].simplex).union(set(simplex))))
                    return

                elif hstype in [ALPHA, VERTEX]:
                    new_vertex = vertex + "-" + str(len(self.hypernetwork[vertex].simplex) + 1)
                    partOf.update(vertex)
                    self.hypernetwork[vertex].simplex.append(new_vertex)
                    vertex = new_vertex

                else:
                    print("SOMETHING WENT WRONG!!")

            elif self.hypernetwork[vertex].hstype == ALPHA:
                # Create a new BETA, move the simplex to a partOf the new BETA
                if condense_all_specials(simplex) != self.hypernetwork[vertex].simplex:
                    tmpHs = self.hypernetwork[vertex]

                    self.add(vertex=vertex + "-1", hstype=tmpHs.hstype, simplex=tmpHs.simplex,
                             R=tmpHs.R, t=tmpHs.t, A=tmpHs.A, N=tmpHs.N, psi=tmpHs.psi, partOf=set(vertex))
                    self.hypernetwork.pop(vertex, None)
                    self.add(vertex=vertex, hstype=BETA, simplex=[vertex + "-1", vertex + "-2"],
                             R=tmpHs.R, t=tmpHs.t, A=tmpHs.A, N=_update_N(tmpHs.N), partOf=tmpHs.partOf)

                    # TODO added the else, this needs testing
                    vertex += "-2"

                else:
                    # TODO why did I include the following
                    partOf.update({vertex})

        # If the simplex of type hsTyoe is found then
        #   replace the new details and all references
        if simplex:
            if vertex or vertex != "":
                search = self.search(hstype=hstype, vertex=vertex, simplex=simplex)

            else:
                search = self.search(hstype=hstype, simplex=simplex)

        else:
            search = self.search(hstype=hstype, vertex=vertex)

        if vertex == "" or not vertex:
            vertex = "hs_{}".format(self._counter)
            self._counter += 1

        if search:
            for v in search:
                if v[:3] == "hs_":
                    # self._hypernetwork[v].simplex = [v if x == v else x for x in self._hypernetwork[v].simplex]
                    self._hypernetwork[v].simplex = [x for x in self._hypernetwork[v].simplex]
                    self._hypernetwork[v].vertex = v
                    self._counter -= 1
                    vertex = v

                self._hypernetwork[vertex].update(R=R, t=t, A=A, N=N, psi=psi)

        else:
            self.add(vertex=vertex, hstype=hstype, simplex=simplex, R=R, t=t, A=A, N=N, psi=psi,
                     partOf=partOf if isinstance(partOf, set) else {partOf})

            if partOf:
                if isinstance(partOf, str):
                    if partOf in self._hypernetwork:
                        self._hypernetwork[partOf].simplex.append(vertex)

                    else:
                        log.error("insert: partOf error.")
                        raise HnInsertError

            for v in simplex:
                if isinstance(v, dict):
                    key = list(v.keys())[0]
                    self.add(vertex=v[key], hstype=VERTEX, partOf={vertex})

                else:
                    self.add(vertex=v, hstype=VERTEX, partOf={vertex})

        for v in simplex:
            if isinstance(v, dict):
                key = list(v.keys())[0]
                v = v[key]

            if v in self._hypernetwork:
                self._hypernetwork[v].partOf.add(vertex)

        return vertex
        
    def update(self):
        pass

    def parse(self, hypernet):
        class _hypersimplex:
            hs_name = ""
            hs_type = NONE
            hs_simplex = []
            hs_R = ""
            hs_t = -1
            hs_A = set()
            hs_N = ""
            hs_psi = ""
            hs_partOf = set()
            hs_where = ""

        class _relation:
            hs_R = ""
            hs_where = []

        def _parse_hs(_hs):
            for hs_k, hs_v in _hs.items():
                if hs_k == "VAL":
                    _hypersimplex.hs_name = hs_v

                elif hs_k == "VERTEX":
                    _hypersimplex.hs_type = str_to_hstype(hs_k)

                elif hs_k in ["ALPHA", "BETA"]:
                    _hypersimplex.hs_type = str_to_hstype(hs_k)

                    if isinstance(hs_v, str):
                        _hypersimplex.hs_simplex.append(hs_v)

                    else:
                        for v in hs_v:
                            if isinstance(v, list):
                                _hypersimplex.hs_simplex.append(self.parse(v))
                            else:
                                _hypersimplex.hs_simplex.append(v)

                elif hs_k in ["EMPTY_ALPHA", "EMPTY_BETA"]:
                    _hypersimplex.hs_v = hs_v

                elif hs_k == "R":
                    _relation.hs_R = hs_v
                    _hypersimplex.hs_R = hs_v

                elif hs_k == "SEQ":
                    # TODO needs fully testing
                    _hypersimplex.hs_simplex.append({"SEQ": hs_v})

                elif hs_k == "t":
                    _hypersimplex.hs_t = hs_v

                elif hs_k == "A":
                    _hypersimplex.hs_A = hs_v

                elif hs_k == "N":
                    _hypersimplex.hs_N = hs_v

                elif hs_k == "psi":
                    _hypersimplex.hs_psi = hs_v

                elif hs_k == "TYPE":
                    print("\tTYPE:" + str(hs_v))

                elif hs_k == "TYPED":
                    print("\tTYPED:" + str(hs_v))

                elif hs_k == "WHERE":
                    _relation.hs_where = hs_v

                elif hs_k == "DERIVED":
                    _hypersimplex.hs_where = "DERIVED"

            return _hypersimplex.hs_name

        # End _parse_hs

        def _clear():
            _hypersimplex.hs_name = ""
            _hypersimplex.hs_type = NONE
            _hypersimplex.hs_simplex = []
            _hypersimplex.hs_R = ""
            _hypersimplex.hs_t = -1
            _hypersimplex.hs_A = set()
            _hypersimplex.hs_N = ""
            _hypersimplex.hs_psi = ""
            _hypersimplex.hs_partOf = set()

            _relation.hs_R = ""
            _relation.hs_where = []
        # End _clear

        name = ""

        _clear()

        for hn in hypernet:
            if isinstance(hn, dict):
                _parse_hs(hn)
            else:
                for hs in hn:
                    _parse_hs(hs)

            if _hypersimplex.hs_type != NONE:
                name = self.insert(vertex=_hypersimplex.hs_name,
                                   hstype=_hypersimplex.hs_type,
                                   simplex=_hypersimplex.hs_simplex,
                                   R=_hypersimplex.hs_R,
                                   t=_hypersimplex.hs_t,
                                   A=_hypersimplex.hs_A,
                                   N=_hypersimplex.hs_N,
                                   psi=_hypersimplex.hs_psi,
                                   partOf=_hypersimplex.hs_partOf)

                if _relation.hs_where:
                    self.relations[_relation.hs_R] = _relation.hs_where

                _clear()

        return name

    def search(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, A=None, N="", partOf=None):
        res = []

        for node in self._hypernetwork.values():
            fail = False
            found = False

            if vertex != "" and not fail:
                if node.vertex == vertex:
                    found = True
                else:
                    fail = True

            if simplex and not fail:
                if hstype in [VERTEX]:
                    if node.simplex == simplex:
                        found = True
                    else:
                        fail = True

                elif hstype == ALPHA:
                    if node.simplex == simplex:
                        found = True
                    else:
                        fail = True

                elif hstype == BETA:
                    if node.simplex \
                            and simplex \
                            and set(node.simplex).intersection(set(simplex)) == set(node.simplex):
                        found = True
                    else:
                        fail = True

                else:
                    fail = True

            # TODO needs more work when we implement full R functionality
            if R and not fail:
                # if node.R == R or re.search(R, node.R):
                if re.search(R, node.R):
                    found = True
                else:
                    fail = True

            # TODO needs more work when we implement full T functionality
            if t >= 0 and not fail:
                if node.t == t:
                    found = True
                else:
                    fail = True

            if N and not fail:
                # if N == node.N or re.match(N, node.N):
                if re.match(N, node.N):
                    found = True
                else:
                    fail = True

            # TODO needs more work when we understand partOf better
            # if partOf:
            #     ...

            if A and not fail:
                if node.A.intersection(A):
                    found = True
                else:
                    fail = True

            if found and not fail:
                res.append(node.vertex)

        return res

    def get_subHn(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, A=None, N="", partOf=None):
        class temp:
            Hn = None

        def _get_subHn(_hs):
            if _hs.hstype not in [VERTEX]:
                for v in _hs.simplex:
                    h = self.hypernetwork[v]
                    _get_subHn(h)
                    temp.Hn.add_hs(vertex=v, hs=h)

        temp.Hn = Hypernetwork()
        searchRes = self.search(vertex=vertex, hstype=hstype, simplex=simplex, R=R, t=t, A=A, N=N, partOf=partOf)

        for v in searchRes:
            hs = self._hypernetwork[v]
            temp.Hn.add_hs(vertex=v, hs=hs)
            _get_subHn(hs)

        return temp.Hn

    def get_vertices(self, vertex="", R=""):
        def _get_vertices(_vertex):
            _res = set()

            if self._hypernetwork[_vertex].hstype in [ALPHA, BETA]:
                _res.add(_vertex)
                for v in self._hypernetwork[_vertex].simplex:
                    _res = _res.union(_get_vertices(v))

            elif self._hypernetwork[_vertex].hstype in [VERTEX]:
                _res.add(self._hypernetwork[_vertex].vertex)

            else:
                log.error("get_vertices: found an unknown Hs Type")
                raise HnUnknownHsType

            return _res

        res = set()

        if R:
            vertices = self.search(R=R)
        elif vertex:
            vertices = self.search(vertex=vertex)
        else:
            vertices = self._hypernetwork.keys()

        for vert in vertices:
            res = res.union(_get_vertices(vert))

        return list(res)

    # def union(self, hs):
        # if self.hypernetwork[hstype == hs.hstype:
        #     for v in hs.
        #         print()
        # pass

    # def intersection(self, hs):
    #     if self.hstype == hs.hstype:
    #         for v in hs.simplex:
    #
    #     pass

    @property
    def soup(self):
        return list(self.hypernetwork.keys())

    def _dump(self):
        for (k, v) in self._hypernetwork.items():
            print(v._dump())

    def __getitem__(self, item):
        return self._hypernetwork[item]

    def __str__(self):
        res = ""

        for (key, hs) in self.hypernetwork.items():
            if hs.hstype not in [NONE, VERTEX]:
                res = res + str(hs) + "\n"

        return res

    def test_str(self):
        def _test_str(vertex):
            simplex = self.hypernetwork[remove_special(vertex)]

            _res = (simplex.vertex + "=") if simplex.vertex else ""

            if simplex.hstype == ALPHA:
                _res += "<"
                for v in simplex.simplex:
                    _res += _test_str(v)
                    _res += ", "

                _res += ("; R" + ("_" + simplex.R) if simplex.R != " " else "") if simplex.R else ""
                _res += ("; t_" + str(simplex.t)) if simplex.t > -1 else ""
                _res += ("; A(" + str(simplex.A) + ")") if simplex.A else ""
                if simplex.N:
                    _res += ">^" + simplex.N + ", "
                else:
                    _res += ">, "

            elif simplex.hstype == BETA:
                _res += "{"
                for v in simplex.simplex:
                    _res += _test_str(v)
                    _res += ", "

                _res += ("; t_" + str(simplex.t)) if simplex.t > -1 else ""
                if simplex.N:
                    _res += "}^" + simplex.N
                else:
                    _res += "}"

            elif simplex.hstype in [VERTEX]:
                return simplex.vertex

            return _res

        # End _test_str

        res = ""
        peaks = get_peaks(self._hypernetwork)

        for peak in peaks:
            res += _test_str(peak)

        # A cheat, but it works
        res = res.replace(", }", "}")
        res = res.replace(", >", ">")
        res = res.replace(", >", ">")
        res = res.replace(", ,", ",")
        res = res.replace(", ;", ";")
        res = res.replace(">, }", ">}")
        res = res.replace(", ,", ",")

        if res[-2:] == ", ":
            res = res[:-2]

        return res
