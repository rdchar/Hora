import copy
import logging
import re
from pprint import pprint

from networkx import intersection

from hypernetworks.core.HTConfig import hs_override_hs_type
from hypernetworks.utils.HTSearch import bottom_up
from hypernetworks.core.HTErrors import HnVertexNoFound, HnUnknownHsType, HnInsertError, HnRMissMatch, \
    HnTypeOrSimplexSizeMismatch, HnHsNotExistInHn
from hypernetworks.core.HTTypes import Types
from hypernetworks.core.Hypersimplex import NONE, ALPHA, BETA, VERTEX, PROPERTY, Hypersimplex, str_to_hstype, \
    UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE, HS_HYPER_PN, HS_STANDARD, HS_ACTIVITY
from hypernetworks.utils.HTPaths import get_peaks
from hypernetworks.utils.HTTools import remove_special


UP = 1
DOWN = -1


class Hypernetwork:
    _counter = 0

    def __init__(self, name="Unnamed", hs_expansion=True):
        self._hs_expansion = hs_expansion
        self._hypernetwork = dict()
        self._boundary_exclusions = dict()
        self._name = name
        self._types = Types()
        self._relations = dict()
        self._psis = dict()
        self._psi_invs = dict()
        self._phis = dict()
        self._phi_invs = dict()

    @property
    def hs_expansion(self):
        return self._hs_expansion

    @hs_expansion.setter
    def hs_expansion(self, hs_expansion):
        self._hs_expansion = hs_expansion

    @property
    def counter(self):
        return self._counter

    @property
    def name(self):
        return self._name

    @property
    def types(self):
        return self._types

    @property
    def hypernetwork(self):
        return self._hypernetwork

    @property
    def relations(self):
        return self._relations

    @property
    def psis(self):
        return self._psis

    @property
    def psi_invs(self):
        return self._psi_invs

    @property
    def phis(self):
        return self._phis

    @property
    def phi_invs(self):
        return self._phi_invs

    @property
    def empty(self):
        return len(self._hypernetwork) == 0

    @property
    def boundary_exclusions(self):
        return self._boundary_exclusions

    def is_empty(self):
        return len(self._hypernetwork) == 0

    def _create_hs(self, _hn, vertex, hs_class=HS_STANDARD, hstype=VERTEX, simplex=None,
                   R="", t=-1, C=None, B=None, N="N",
                   psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):

        # TODO this should be injected at start of application.
        if hs_class == HS_HYPER_PN:
            from hyperPn.core.hyperPn import HPnHypersimplex
            return HPnHypersimplex(self, vertex=vertex, hs_class=hs_class, hstype=hstype, simplex=simplex,
                                   R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                   partOf=partOf, traffic=traffic, coloured=coloured)

        if hs_class == HS_ACTIVITY:
            from core.ActivityHn import ActivityHypersimplex
            return ActivityHypersimplex(self, vertex=vertex, hs_class=hs_class, hstype=hstype, simplex=simplex,
                                   R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                   partOf=partOf, traffic=traffic, coloured=coloured)

        return Hypersimplex(self, vertex=vertex, hstype=hstype, simplex=simplex, R=R, t=t, C=C, B=B, N=N,
                            psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                            partOf=partOf, traffic=traffic, coloured=coloured)

    def change_hs_class(self, hs_name, new_hs_class):
        if hs_name not in self._hypernetwork:
            raise HnHsNotExistInHn

        hs = self._hypernetwork[hs_name]
        if new_hs_class == HS_HYPER_PN:
            from hyperPn.core.hyperPn import HPnHypersimplex
            new_hs = HPnHypersimplex(self, vertex=hs.vertex, hs_class=new_hs_class, hstype=hs.hstype,
                                     simplex=hs.simplex, R=hs.R, t=hs.t, C=hs.C, B=hs.B, N=hs.N,
                                     psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                                     partOf=hs.partOf, traffic=hs.traffic, coloured=hs.coloured)

            del self._hypernetwork[hs_name]
            self._hypernetwork[hs_name] = new_hs

        if new_hs_class == HS_ACTIVITY:
            from core.ActivityHn import ActivityHypersimplex
            new_hs = ActivityHypersimplex(self, vertex=hs.vertex, hs_class=new_hs_class, hstype=hs.hstype,
                                     simplex=hs.simplex, R=hs.R, t=hs.t, C=hs.C, B=hs.B, N=hs.N,
                                     psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                                     partOf=hs.partOf, traffic=hs.traffic, coloured=hs.coloured)

            del self._hypernetwork[hs_name]
            self._hypernetwork[hs_name] = new_hs


    def load_hs(self, hs):
        self._hypernetwork.update({hs.vertex: hs})

    def _add_func_collections(self, R, psi="", psi_inv="", phi="", phi_inv=""):
        if R:
            if isinstance(R, str):
                if R != " ":
                    self._relations[R] = None
            else:
                if R.name and R.name != " ":
                    self._relations[R.name] = None

        if psi:
            self.psis[psi] = None

        if psi_inv:
            self.psi_invs[psi_inv] = None

        if phi:
            self.phis[phi] = None

        if phi_inv:
            self.phi_invs[phi_inv] = None


    def _add(self, vertex, hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="N",
             psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):

        if vertex in self._hypernetwork:
            # Update an existing node
            temp = self._hypernetwork[vertex]

            if temp.hstype not in [NONE, VERTEX, PROPERTY] and not hs_override_hs_type:
                hstype = temp.hstype

            if temp.simplex and not simplex:
                simplex = temp.simplex[:]

            if temp.R.name == "" and (R if isinstance(R, str) else R.name) == "":
                R = temp.R

            if temp.C and not C:
                C = temp.C.copy()

            if temp.B and not B:
                B = temp.B.copy()

            if temp.N and N == "":
                N = temp.N

            if temp.psi != "" and psi == "":
                psi = temp.psi

            if temp.psi_inv != "" and psi_inv == "":
                psi_inv = temp.psi_inv

            if temp.phi != "" and phi == "":
                phi = temp.phi

            if temp.phi_inv != "" and phi_inv == "":
                phi_inv = temp.phi_inv

            if temp.partOf and not partOf:
                partOf = temp.partOf.copy()

            if temp.traffic and traffic is None:
                traffic = temp.traffic

            if temp.coloured and coloured is None:
                coloured = temp.coloured

            if temp.hstype == PROPERTY:
                # TODO not sure it is correct
                hstype = temp.hstype

            temp.update(hstype=hstype, simplex=simplex, R=R, t=t, C=C, B=B, N=N,
                        psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                        partOf=partOf, traffic=traffic, coloured=coloured)

            self._hypernetwork[vertex] = temp

            if hs_class != self._hypernetwork[vertex].hs_class:
                self.change_hs_class(vertex, hs_class)

        else:
            hs = self._create_hs(self, vertex=vertex, hs_class=hs_class, hstype=hstype, simplex=simplex,
                                 R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                 partOf=partOf, traffic=traffic, coloured=coloured)

            self._hypernetwork.update({vertex: hs})

        self._add_func_collections(R, psi, psi_inv, phi, phi_inv)

    def insert_hs(self, vertex="", hs=None):
        if vertex:
            vertex = hs.vertex

        self.insert(vertex, hstype=hs.hstype, simplex=hs.simplex, R=hs.R, t=hs.t, C=hs.C, B=hs.B,
                    N=hs.N, psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                    traffic=hs.traffic, coloured=hs.coloured)

    def delete(self, vertex="", R="", del_children=False, B=""):
        def _delete_vertex(_vertex):
            for _vert in self._hypernetwork[_vertex].simplex:
                if _vert in self._hypernetwork:
                    if _vertex in self._hypernetwork[_vert].partOf:
                        self._hypernetwork[_vert].partOf.remove(_vertex)

                if del_children:
                    _delete_vertex(_vert)

            # Removes all instances of the vertex.
            for _whole in self._hypernetwork[_vertex].partOf:
                for temp in self._hypernetwork[_whole].simplex:
                    _part = remove_special(temp)
                    if _part == _vertex:
                        self._hypernetwork[_whole].simplex.remove(temp)

            del self._hypernetwork[_vertex]
        # End _delete_vertex

        def _find_B_peaks():
            peaks = []

            def _find_peak(_vertex):
                if len(self._hypernetwork[_vertex].partOf) > 0:
                    for whole in self._hypernetwork[_vertex].partOf:
                        if B in self._hypernetwork[whole].B:
                            _find_peak(whole)

                        else:
                            peaks.append(whole)

                else:
                    peaks.append(_vertex)

            _find_peak(vertex)

            return peaks
        # End _find_B_peaks

        def _delete_boundary():
            def _delete_vertex_from_boundary(_vertex, _parent):
                print("HELLO XXXX")
                if B in self._hypernetwork[_vertex].B:
                    print("\tHELLO 2", _vertex, "from", _parent, self._hypernetwork[_vertex].simplex)

                    if _vertex in self._hypernetwork:
                        if len(self._hypernetwork[_vertex].B) == 1:
                            if _vertex == vertex or (B in self._hypernetwork[_parent].B and _parent == vertex):
                                self._hypernetwork[_parent].simplex.remove(_vertex)

                            if len(self._hypernetwork[_vertex].partOf) == 1:
                                del self._hypernetwork[_vertex]

                            else:
                                print("\t\tHELLO 5", _vertex, "from", _parent)
                                # self._hypernetwork[_parent].simplex.remove(_vertex)
                                self._hypernetwork[_vertex].partOf.remove(_parent)

                        else:
                            print("\t\tHELLO 4", _vertex)
                            self._hypernetwork[_vertex].B.remove(B)

                else:
                    print("\tHELLO 3", _vertex, "from", _parent, self._hypernetwork[_vertex].simplex)
                    if _vertex == vertex:
                        if _parent in self._hypernetwork and _vertex in self._hypernetwork[_parent].simplex:
                            self._hypernetwork[_parent].simplex.remove(_vertex)
            # End _delete_vertex_from_boundary

            def _delete_from_boundary(_vertex, _parent):
                if _vertex in self._hypernetwork:
                    for _vert in self._hypernetwork[_vertex].simplex:
                        print("HELLO 1", _vert, "from", _vertex, self._hypernetwork[_vertex].simplex)
                        _delete_from_boundary(_vert, _vertex)

                        if _vert in self._hypernetwork:
                            print("\t\tHELLO 10", _vert, self._hypernetwork[_vert].B, B, self._hypernetwork[_vert].partOf)
                            if del_children or B in self._hypernetwork[_vert].B:
                                _delete_vertex_from_boundary(_vert, _vertex)
            # End _delete_from_boundary

            # peaks = _find_B_peaks()
            peaks = self._hypernetwork[vertex].partOf

            for peak in peaks:
                _delete_from_boundary(vertex, peak)

                if vertex in self._hypernetwork[peak].simplex:
                    self._hypernetwork[peak].simplex.remove(vertex)

                if vertex in self._hypernetwork:
                    if B in self._hypernetwork[vertex].B:
                        if len(self._hypernetwork[vertex].B) == 1:
                            del self._hypernetwork[vertex]
                        else:
                            self._hypernetwork[vertex].B.remove(B)

        # End _delete_boundary

        # TODO may need more work
        if R:
            vertices = self.search(R=R)
            for vert in vertices:
                _delete_vertex(_vertex=vert)

        elif B:
            if vertex and vertex in self._hypernetwork:
                _delete_boundary()

        elif vertex and vertex in self._hypernetwork:
            _delete_vertex(_vertex=vertex)

        else:
            raise HnVertexNoFound

    def _update_N(self, _N, _direction=UP):
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

    def get_semantic_boundaries(self):
        semantic_boundaries = set()

        for name in self._hypernetwork:
            for sb in self._hypernetwork[name].B:
                semantic_boundaries.add(sb)

        return semantic_boundaries

    def insert(self, vertex="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None,
               N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None,
               boundary_exclusions=None):

        def _remove_cyclic():
            temp = list(set(self._hypernetwork[vertex].simplex).intersection(self._hypernetwork[vertex].partOf))

            if temp:
                for v in simplex:
                    if isinstance(v, dict):
                        v = list(v.values())[0]

                    if v in temp:
                        self._hypernetwork[vertex].simplex.remove(v)
        # End _remove_cyclic

        def _insert(partOf={}, hs_class=hs_class):
            if vertex in self._hypernetwork:
                if hstype == BETA:
                    partOf = partOf.union(self._hypernetwork[vertex].partOf)

            # TODO add cyclic removal code
            self._add(vertex=vertex, hs_class=hs_class, hstype=hstype, simplex=simplex,
                      R=R, t=t, C=C, B=B, N=N,
                      psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                      partOf=partOf if isinstance(partOf, set) else {partOf}, traffic=traffic, coloured=coloured)

            for i, v in enumerate(simplex):
                if "PROPERTY" in v:
                    self._hypernetwork[vertex].simplex[i] = v["PROPERTY"]

            if partOf:
                if isinstance(partOf, str):
                    if partOf in self._hypernetwork:
                        self._hypernetwork[partOf].simplex.append(vertex)

                    else:
                        logging.error("insert: partOf error.")
                        raise HnInsertError

            for i, v in enumerate(simplex):
                child_B = B.union(self._hypernetwork[vertex].B) if B else self._hypernetwork[vertex].B

                if isinstance(v, dict):
                    if "PROPERTY" in v:
                        self._add(vertex=v["PROPERTY"], hs_class=hs_class, hstype=PROPERTY, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)
                    else:
                        key = list(v.keys())[0]

                        self._add(vertex=v[key], hs_class=hs_class, hstype=VERTEX, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)

                else:
                    if hstype:
                        self._add(vertex=v, hs_class=hs_class, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)

                    else:
                        self._add(vertex=v, hs_class=hs_class, hstype=VERTEX, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)
        # End _insert

        if simplex is None:
            simplex = []

        if partOf is None:
            partOf = set()

        R_comparision = True
        do_search = True

        if hstype in [PROPERTY]:
            if vertex in self.hypernetwork:
                self._hypernetwork[vertex].update(vertex=vertex, hstype=hstype, R=R, t=t, C=C, B=B, N=N,
                                                  psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                                  traffic=traffic, coloured=coloured)

            else:
                self._add(vertex=vertex, hs_class=hs_class, hstype=hstype, simplex=simplex,
                          R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                          partOf=partOf if isinstance(partOf, set) else {partOf}, traffic=traffic, coloured=coloured)
            # return vertex

        if vertex in self.hypernetwork:
            if isinstance(R, str):
                if R and self._hypernetwork[vertex].R.name:
                    R_comparision = R == self._hypernetwork[vertex].R.name
            else:
                if R.name and self._hypernetwork[vertex].R.name:
                    R_comparision = R.name == self._hypernetwork[vertex].R.name

            # TODO new rules that need testing
            # if self.hypernetwork[vertex].hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE] \_handle_Hs_union_dups
            #         and self.hypernetwork[vertex].hstype == hstype:
            if self.hypernetwork[vertex].hstype in [BETA] \
                    and self.hypernetwork[vertex].simplex != simplex and simplex:
                # Add to BETA
                if hstype == BETA:
                    if not R_comparision:
                        raise HnRMissMatch

                    simplex = list(sorted(set(self.hypernetwork[vertex].simplex).union(set(simplex))))
                    # self.hypernetwork[vertex].simplex = \
                    #     list(sorted(set(self.hypernetwork[vertex].simplex).union(set(simplex))))

                    _insert(partOf, hs_class=hs_class)
                    return

                elif hstype in [ALPHA, VERTEX, PROPERTY, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                    new_vertex = vertex + "@" + str(len(self.hypernetwork[vertex].simplex) + 1)
                    partOf.add(vertex)
                    self.hypernetwork[vertex].simplex.append(new_vertex)
                    vertex = new_vertex

                else:
                    print("SOMETHING WENT WRONG!!")

            elif self.hypernetwork[vertex].hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                # Create a new BETA, move the simplex to a partOf the new BETA
                if self.hypernetwork[vertex].hstype == hstype:
                    if self.hypernetwork[vertex]._validate_alpha_R(simplex, R, R_comparision):
                        (simplex, R) = self.hypernetwork[vertex]._handle_alpha_diff_R(simplex=simplex, R=R)
                    else:
                        if self.hs_expansion:
                            (simplex, R) = self.hypernetwork[vertex]._handle_hs_expansion(simplex=simplex, R=R)
                        else:
                            raise HnRMissMatch

                if hstype == UNION_ALPHA:
                    (hstype, simplex, R) = self.hypernetwork[vertex]._handle_alpha_union(hstype=hstype,
                                                                                         simplex=simplex, R=R)

                if hstype not in [VERTEX, PROPERTY] and simplex != self.hypernetwork[vertex].simplex:
                    vertex = self.hypernetwork[vertex]._handle_Hs_union_dups(hstype=hstype, simplex=simplex,
                                                                             R=R, t=t, C=C, B=B, N=N,
                                                                             psi=psi, psi_inv=psi_inv,
                                                                             phi=phi, phi_inv=phi_inv,
                                                                             partOf=partOf, traffic=traffic,
                                                                             coloured=coloured)
                    do_search = False

                else:
                    if R:
                        if not self._hypernetwork[vertex].R.is_equal(R):
                            R = self._hypernetwork[vertex].R

                    if self._hypernetwork[vertex].B != B:
                        if B:
                            B = self._hypernetwork[vertex].B.union(B)

                    partOf.add(vertex)
            elif self.hypernetwork[vertex].hstype in [PROPERTY]:
                self._hypernetwork[vertex].update(vertex=vertex, hstype=hstype, hs_class=hs_class,
                                                  R=R, t=t, C=C, B=B, N=N,
                                                  psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                                  traffic=traffic, coloured=coloured)

        # TODO This has been disabled because it didn't work!
        # if R:
        #     search = self.search(hstype=hstype, R=R)
        #     # TODO need to investigate this ...
            # if search:
            #     if hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
            #         for v in search:
            #             if hstype != self._hypernetwork[v].hstype or \
            #                     len(simplex) != len(self._hypernetwork[v].simplex):
            #                 raise HnTypeOrSimplexSizeMismatch
            #
                # TODO need to investigate this ...
                # elif hstype in [BETA]:
                #     for v in search:
                #         if hstype != self._hypernetwork[v].hstype:
                #             raise HnTypeOrSimplexSizeMismatch

        # If the simplex of type hsTyoe is found then
        #   replace the new details and all references
        search = []
        if do_search:
            if simplex:
                if vertex or vertex != "":
                    search = self.search(hstype=hstype, vertex=vertex, simplex=simplex)
                else:
                    search = self.search(hstype=hstype, simplex=simplex)

            else:
                if hstype not in [PROPERTY]:
                    search = self.search(hstype=hstype, vertex=vertex)

        if vertex == "" or not vertex:
            if hstype not in [PROPERTY]:
                vertex = "@Hs_{}@".format(self._counter)
                self._counter += 1

        if search:
            for v in search:
                # TODO need to keep an eye on this, it was implemented for a reason
                if v[:4] == "@Hs_" and R_comparision:
                    # self._hypernetwork[v].simplex = [v if x == v else x for x in self._hypernetwork[v].simplex]
                    # self._hypernetwork[v].simplex = [x for x in self._hypernetwork[v].simplex]
                    # self._hypernetwork[v].vertex = v

                    for part in self._hypernetwork[v].partOf:
                        for i, val in enumerate(self._hypernetwork[part].simplex):
                            if val == v:
                                self._hypernetwork[part].simplex[i] = vertex

                    # self._counter -= 1
                    self._hypernetwork[vertex] = self._hypernetwork.pop(v)
                else:
                    vertex = v

                self._hypernetwork[vertex].update(vertex=vertex, R=R, t=t, C=C, B=B, N=N,
                                                  psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                                  traffic=traffic, coloured=coloured)

        else:
            # TODO added this to union the partOf, not sure if it is correct, needs testing
            if hstype not in [PROPERTY]:
                _insert(partOf, hs_class=hs_class)  # TODO this is new and not fully tested

        for v in simplex:
            if isinstance(v, dict):
                key = list(v.keys())[0]
                v = v[key]

            if v in self._hypernetwork:
                self._hypernetwork[v].partOf.add(vertex)

        # Remove cyclic references
        # _remove_cyclic()
        if not boundary_exclusions:
            boundary_exclusions = self._boundary_exclusions

        self.apply_boundary_exclusions(boundary_exclusions)

        return vertex

    # TODO Needs testing properly
    def union(self, _hn):
        for name, hs in _hn.hypernetwork.items():
            # hs = _hn.hypernetwork[name]
            if name in self._hypernetwork:
                traffic = hs._union_traffic(hs.traffic)
            else:
                traffic = hs.traffic

            if name in self._hypernetwork:
                coloured = hs._union_coloured(hs.traffic)
            else:
                coloured = hs.coloured

            self.insert(vertex=name, hs_class=hs.hs_class, hstype=hs.hstype, simplex=hs.simplex,
                        R=hs.R, t=hs.t, C=hs.C, B=hs.B,
                        psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                        traffic=traffic, coloured=coloured)

            self._add_func_collections(hs.R, hs.psi, hs.psi_inv, hs.phi, hs.phi_inv)

        return self

    def copy(self, _hn):
        self._hs_expansion = _hn.hs_expansion

        self._hypernetwork = {}
        for name, hs in _hn.hypernetwork.items():
            self._hypernetwork.update({name: copy.deepcopy(hs)})

        self._boundary_exclusions = _hn.boundary_exclusions.copy()
        self._name = _hn.name
        self._types = copy.deepcopy(_hn.types)
        self._relations = _hn.relations.copy()
        self._psis = _hn.psis.copy()
        self._psi_invs = _hn.psi_invs.copy()
        self._phis = _hn.phis.copy()
        self._phi_invs = _hn.phi_invs.copy()

        return self

    # TODO Needs testing properly
    def intersection(self, hn, inc_whole_beta=True):
        new_hn = Hypernetwork()

        for name, hs in self.hypernetwork.items():
            simplex = []
            if name in hn.hypernetwork and hs.R.is_equal(hn.hypernetwork[name].R):
                if not inc_whole_beta and hs.hstype in [BETA]:
                    for vertex in hs.simplex:
                        if vertex in hn.hypernetwork:
                            simplex.append(vertex)

                else:
                    simplex = hs.simplex

                new_hn.insert(hs.vertex, hs_class=hs.hs_class, hstype=hs.hstype, simplex=simplex,
                              R=hs.R, t=hs.t, C=hs.C, B=hs.B, psi=hs.psi, psi_inv=hs.psi_inv,
                              phi=hs.phi, phi_inv=hs.phi_inv,
                              traffic=hs.traffic, coloured=hs.coloured)

        self._hypernetwork.clear()

        for name, hs in new_hn.hypernetwork.items():
            self._hypernetwork.update({name: hs})

        return new_hn

    def update(self, vertex="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None,
               N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):
        pass

    # def preparse(self, hypernet):
    #     return

    def parse(self, hypernet):
        class _hypersimplex:
            hs_name = ""
            hs_type = NONE
            hs_simplex = []
            hs_R = ""
            hs_t = -1
            hs_C = []
            hs_B = set()
            hs_N = ""
            hs_psi = ""
            hs_psi_inv = ""
            hs_phi = ""
            hs_phi_inv = ""
            hs_partOf = set()
            hs_where = ""
            hs_traffic = None
            hs_coloured = None
            hs_special = NONE

        class _relation:
            hs_R = None
            hs_where = []

        def _parse_hs(_hs):
            for hs_k, hs_v in _hs.items():
                if hs_k == "VAL":
                    _hypersimplex.hs_name = hs_v

                elif hs_k in ["VERTEX", "PROPERTY"]:
                    _hypersimplex.hs_type = str_to_hstype(hs_k)

                elif hs_k in ["ALPHA", "BETA", "UNION_ALPHA", "IMMUTABLE_ALPHA", "SEQUENCE"]:
                    _hypersimplex.hs_type = str_to_hstype(hs_k)

                    if isinstance(hs_v, str) or isinstance(hs_v, dict):
                        _hypersimplex.hs_simplex.append(hs_v)

                    else:
                        for v in hs_v:
                            if isinstance(v, list):
                                _hypersimplex.hs_simplex.append(self.parse(v))
                            elif isinstance(v, dict):
                                if "SEQUENCE" in v:
                                    _hypersimplex.hs_simplex.append(self.parse(v))
                                else:
                                    _hypersimplex.hs_simplex.append(v)
                            else:
                                _hypersimplex.hs_simplex.append(v)

                elif hs_k in ["EMPTY_ALPHA", "EMPTY_BETA"]:
                    _hypersimplex.hs_v = hs_v

                elif hs_k == "R":
                    _relation.hs_R = hs_v
                    _hypersimplex.hs_R = hs_v

                elif hs_k == "t":
                    _hypersimplex.hs_t = hs_v

                elif hs_k == "COORD":
                    _hypersimplex.hs_C = hs_v

                elif hs_k == "B":
                    _hypersimplex.hs_B = hs_v

                elif hs_k == "N":
                    _hypersimplex.hs_N = hs_v

                elif hs_k == "psi":
                    _hypersimplex.hs_psi = hs_v

                elif hs_k == "psi_inv":
                    _hypersimplex.hs_psi_inv = hs_v

                elif hs_k == "phi":
                    _hypersimplex.hs_phi = hs_v

                elif hs_k == "phi_inv":
                    _hypersimplex.hs_phi_inv = hs_v

                elif hs_k == "TYPE":
                    print("\tTYPE:" + str(hs_v))

                elif hs_k == "TYPED":
                    print("\tTYPED:" + str(hs_v))

                elif hs_k in ["RELATION", "WHERE"]:
                    _relation.hs_R = hs_v[0]['R']

                    if _relation.hs_R not in self._relations:
                        _relation.hs_where = hs_v[1:]
                    else:
                        if not self._relations[_relation.hs_R]:
                            _relation.hs_where = hs_v[1:]
                        else:
                            if _relation.hs_where != self._relations[_relation.hs_R]:
                                print("WARNING: Duplicate relation", _relation.hs_R,
                                      "has new definition:", _relation.hs_where,
                                      "does not match current:", self._relations[_relation.hs_R],
                                      "the current definition will be kept.")

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
            _hypersimplex.hs_C = []
            _hypersimplex.hs_B = set()
            _hypersimplex.hs_N = ""
            _hypersimplex.hs_psi = ""
            _hypersimplex.hs_phi = ""
            _hypersimplex.hs_partOf = set()
            _hypersimplex.hs_traffic = None
            _hypersimplex.hs_coloured = None

            _relation.hs_R = ""
            _relation.hs_where = []
        # End _clear

        name = ""
        _clear()

        # pprint(hypernet)
        # self.preparse(hypernet)

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
                                   C=_hypersimplex.hs_C,
                                   B=_hypersimplex.hs_B,
                                   N=_hypersimplex.hs_N,
                                   psi=_hypersimplex.hs_psi,
                                   psi_inv=_hypersimplex.hs_psi_inv,
                                   phi=_hypersimplex.hs_phi,
                                   phi_inv=_hypersimplex.hs_phi_inv,
                                   partOf=_hypersimplex.hs_partOf,
                                   traffic=None,
                                   coloured=None)

                if _relation.hs_where:
                    self.relations[_relation.hs_R] = _relation.hs_where

                _clear()

            else:
                if _relation.hs_where:
                    self.relations[_relation.hs_R] = _relation.hs_where[0] \
                        if len(_relation.hs_where) == 1 else _relation.hs_where

        return name

    def search(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="", partOf=None):
        res = []

        for node in self._hypernetwork.values():
            fail = False
            found = False

            if vertex and not fail:
                if node.vertex == vertex:
                    found = True
                else:
                    fail = True

            if (simplex and not fail) or (simplex and vertex != node.vertex):
                if hstype in [VERTEX, PROPERTY]:
                    if node.simplex == simplex:
                        found = True
                    else:
                        fail = True

                elif hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                    if node.simplex == simplex:
                        if node.vertex[:4] == "@Hs_":
                            found = True
                            fail = vertex == node.vertex

                        else:
                            fail = True
                    else:
                        fail = True

                elif hstype == BETA:
                    temp_simplex = [x["PROPERTY"] if isinstance(x, dict) else x for x in simplex]
                    temp_node_simplex = [x["PROPERTY"] if isinstance(x, dict) else x for x in node.simplex]

                    if node.simplex \
                            and simplex \
                            and set(temp_node_simplex).intersection(set(temp_simplex)) == set(temp_node_simplex):
                        found = True
                    else:
                        fail = True

                else:
                    fail = True

            # TODO needs more work when we implement full R functionality
            if R and not fail:
                # if node.R == R or re.search(R, node.R):
                if re.search(R if isinstance(R, str) else R.name, node.R.name):
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
                # if == node.N or re.match(N, node.N):
                if re.match(N, node.N):
                    found = True
                else:
                    fail = True

            # TODO needs more work when we understand partOf better
            # if partOf:
            #     ...

            if B and not fail:
                if intersection(B):
                    found = True
                else:
                    fail = True

            if found and not fail:
                res.append(node.vertex)

        return res

    def get_subHn(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="", partOf=None):
        class temp:
            Hn = None

        def _get_subHn(_hs):
            if _hs.hstype not in [VERTEX, PROPERTY]:
                for v in _hs.simplex:
                    h = self.hypernetwork[v]
                    _get_subHn(h)
                    temp.Hn.insert_hs(vertex=v, hs=h)

        temp.Hn = Hypernetwork()
        searchRes = self.search(vertex=vertex, hstype=hstype, simplex=simplex, R=R, t=t, C=C, B=B, N=N, partOf=partOf)

        for v in searchRes:
            hs = self._hypernetwork[v]
            temp.Hn.insert_hs(vertex=v, hs=hs)
            _get_subHn(hs)

        return temp.Hn

    def get_vertices(self, vertex="", R=""):
        def _get_vertices(_vertex):
            _res = set()

            if self._hypernetwork[_vertex].hstype in [ALPHA, BETA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                _res.add(_vertex)
                for v in self._hypernetwork[_vertex].simplex:
                    _res = _res.union(_get_vertices(v))

            elif self._hypernetwork[_vertex].hstype in [VERTEX, PROPERTY]:
                _res.add(self._hypernetwork[_vertex].vertex)

            else:
                logging.error("get_vertices: found an unknown Hs Type")
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

    @property
    def soup(self):
        return list(self.hypernetwork.keys())

    def _dump(self):
        for (k, v) in self._hypernetwork.items():
            print(v._dump())

    def __getitem__(self, item):
        if item in self._hypernetwork:
            return self._hypernetwork[item]
        return None

    def __str__(self):
        res = ""

        for key, hs in self.hypernetwork.items():
            if hs.hstype not in [NONE, VERTEX, PROPERTY]:
                res = res + str(hs) + "\n"

        return res

    def remove_from_boundary(self, vertex, boundary):
        def _next(next_hs):
            for name in self._hypernetwork[next_hs].simplex:
                _next(name)

            self._hypernetwork[next_hs].remove_from_boundary(boundary)

            if vertex not in self._boundary_exclusions:
                self._boundary_exclusions.update({vertex: set()})

            self._boundary_exclusions[vertex].add(boundary)

        if vertex in self._hypernetwork:
            _next(vertex)

    def apply_boundary_exclusions(self, boundary_exclusions=None):
        for vertex, exclusion in boundary_exclusions.items():
            for boundary in exclusion:
                self.remove_from_boundary(vertex, boundary)

    def test_str(self):
        def _test_str(vertex):
            simplex = self.hypernetwork[remove_special(vertex)]

            _res = (simplex.vertex + "=") if simplex.vertex else ""

            if simplex.hstype in [ALPHA, UNION_ALPHA, SEQUENCE]:
                _res += "<"
                for v in simplex.simplex:
                    _res += _test_str(v)
                    _res += ", "

                _res += ("; R" + ("_" + simplex.R.name) if simplex.R.name != " " else "") if simplex.R.name else ""
                _res += ("; t_" + str(simplex.t)) if simplex.t > -1 else ""
                _res += ("; B(" + str(simplex.B) + ")") if simplex.B else ""
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

            elif simplex.hstype in [VERTEX, PROPERTY]:
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
