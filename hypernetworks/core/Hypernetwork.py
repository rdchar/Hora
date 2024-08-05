import copy
import logging
import re
from pprint import pprint

from networkx import intersection

from hypernetworks.core.HTConfig import hs_override_hs_type
from hypernetworks.core.HTErrors import HnVertexNoFound, HnUnknownHsType, HnInsertError, HnRMismatch, HnHsNotExistInHn
from hypernetworks.core.HTTypes import Types
from hypernetworks.core.Hypersimplex import NONE, ALPHA, BETA, VERTEX, ANTI_VERTEX, PROPERTY, \
    UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE, HS_HYPER_PN, HS_STANDARD, HS_ACTIVITY, \
    Hypersimplex, str_to_hstype, hstype_to_str
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

    def __len__(self):
        return len(self._hypernetwork)

    def clear(self, name="Unnamed", hs_expansion=False):
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

            if temp.hstype not in [NONE, VERTEX, ANTI_VERTEX, PROPERTY] and not hs_override_hs_type:
                hstype = temp.hstype

            if temp.simplex and not simplex:
                simplex = temp.simplex[:]

            if temp.R.name == "" and (R if isinstance(R, str) else R.name) == "":
                R = temp.R

            if temp.C and not C:
                C = temp.C.copy()

            if temp.B and not B:
                B = temp.B.copy()

            if temp.N and N == "N":
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

            if temp.hstype == ANTI_VERTEX:
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

        def _delete_whole_boundary():
            temp = copy.deepcopy(self._hypernetwork)
            peaks = []

            for name, hs in temp.items():
                if B in hs.B:
                    for parent in hs.partOf:
                        if parent in self._hypernetwork:
                            if len(hs.B) <= 1 and name in self._hypernetwork[parent].simplex:
                                self._hypernetwork[parent].simplex.remove(name)

                    if len(hs.B) == 1:
                        if name in self._hypernetwork:
                            del self._hypernetwork[name]

                    else:
                        self._hypernetwork[name].B.remove(B)

            return peaks

        # End _delete_whole_boundary

        def _delete_boundary():
            def _delete_vertex_from_boundary(_vertex, _parent):
                if _vertex in self._hypernetwork:
                    hs = self._hypernetwork[_vertex]

                    if B in hs.B:
                        if len(hs.B) == 1 and len(hs.partOf) == 1:
                            del self._hypernetwork[_vertex]

                        else:
                            if len(self._hypernetwork[_vertex].partOf) == 1:
                                self._hypernetwork[_vertex].B.remove(B)

                    else:
                        parents = set()
                        for parent in hs.partOf:
                            if parent in self._hypernetwork:
                                if B in self._hypernetwork[parent].B and len(self._hypernetwork[parent].B) == 1:
                                    parents.add(parent)

                        self._hypernetwork[_vertex].partOf = self._hypernetwork[_vertex].partOf.difference(parents)

            # End delete_from_boundary

            def _delete_from_boundary(_vertex, _parent):
                if _vertex in self._hypernetwork:
                    for vert in self._hypernetwork[_vertex].simplex:
                        hs = self._hypernetwork[vert]

                        if B in hs.B:
                            _delete_from_boundary(vert, _vertex)

                        _delete_vertex_from_boundary(vert, _vertex)

                    for vert in self._hypernetwork[_vertex].simplex:
                        if vert not in self._hypernetwork:
                            self._hypernetwork[_vertex].simplex.remove(vert)

            # End _delete_from_boundary

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
            else:
                _delete_whole_boundary()

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

    def get_boundaries(self):
        semantic_boundaries = set()

        for name in self._hypernetwork:
            for sb in self._hypernetwork[name].B:
                semantic_boundaries.add(sb)

        return semantic_boundaries

    def remove_vertices_from_boundary(self, boundary, *vertices):
        for vertex in vertices:
            hs = self._hypernetwork[vertex]

            if boundary in hs.B:
                hs.remove_from_boundary(boundary)

    def add_vertices_to_boundary(self, boundary, vertices):
        for vertex in vertices:
            self._hypernetwork[vertex].add_to_boundary(boundary)

    def insert(self, vertex="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None,
               N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None,
               boundary_exclusions=None, boundary_percolation=True):

        # def _remove_cyclic():
        #     temp = list(set(self._hypernetwork[vertex].simplex).intersection(self._hypernetwork[vertex].partOf))
        #
        #     if temp:
        #         for v in simplex:
        #             if isinstance(v, dict):
        #                 v = list(v.values())[0]
        #
        #             if v in temp:
        #                 self._hypernetwork[vertex].simplex.remove(v)

        # End _remove_cyclic

        def _R_equal():
            if vertex in self._hypernetwork:
                if isinstance(R, str):
                    if R and self._hypernetwork[vertex].R.name:
                        return R == self._hypernetwork[vertex].R.name
                else:
                    if R.name and self._hypernetwork[vertex].R.name:
                        return R.name == self._hypernetwork[vertex].R.name

            return True


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
                elif "ANTI_VERTEX" in v:
                    self._hypernetwork[vertex].simplex[i] = v["ANTI_VERTEX"]

            if partOf:
                if isinstance(partOf, str):
                    if partOf in self._hypernetwork:
                        self._hypernetwork[partOf].simplex.append(vertex)

                    else:
                        logging.error("insert: partOf error.")
                        raise HnInsertError

            for i, v in enumerate(simplex):
                child_B = set()

                if boundary_percolation:
                    child_B = B.union(self._hypernetwork[vertex].B) if B else self._hypernetwork[vertex].B  # TODO B

                if isinstance(v, dict):
                    if "PROPERTY" in v:
                        self._add(vertex=v["PROPERTY"], hs_class=hs_class, hstype=PROPERTY, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)
                    elif "ANTI_VERTEX" in v:
                        self._add(vertex=v["ANTI_VERTEX"], hs_class=hs_class, hstype=ANTI_VERTEX, partOf={vertex},
                                  B=child_B,
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

        R_equal = True
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
            R_equal = _R_equal()
            if R_equal and (hstype in [ALPHA, UNION_ALPHA] and self._hypernetwork[vertex].hstype in [BETA]) or \
                    (hstype in [BETA] and self._hypernetwork[vertex].hstype in [ALPHA, UNION_ALPHA]):
                raise HnRMismatch(f"{R} with Hs/vertex {vertex}.")

            # if isinstance(R, str):
            #     if R and self._hypernetwork[vertex].R.name:
            #         R_equal = R == self._hypernetwork[vertex].R.name
            # else:
            #     if R.name and self._hypernetwork[vertex].R.name:
            #         R_equal = R.name == self._hypernetwork[vertex].R.name

            # TODO new rules that need testing
            # if self.hypernetwork[vertex].hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE] \_handle_Hs_union_dups
            #         and self.hypernetwork[vertex].hstype == hstype:
            if self.hypernetwork[vertex].hstype in [BETA] \
                    and self.hypernetwork[vertex].simplex != simplex and simplex:
                # Add to BETA
                if hstype == BETA:
                    if not R_equal:
                        raise HnRMismatch(f"{R} with Hs/vertex {vertex}.")

                    simplex = list(sorted(set(self.hypernetwork[vertex].simplex).union(set(simplex))))
                    # self.hypernetwork[vertex].simplex = \
                    #     list(sorted(set(self.hypernetwork[vertex].simplex).union(set(simplex))))

                    _insert(partOf, hs_class=hs_class)
                    return

                elif hstype in [ALPHA, VERTEX, ANTI_VERTEX, PROPERTY, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                    new_vertex = vertex + "@" + str(len(self.hypernetwork[vertex].simplex) + 1)
                    partOf.add(vertex)
                    self.hypernetwork[vertex].simplex.append(new_vertex)
                    vertex = new_vertex

                else:
                    print("SOMETHING WENT WRONG!!")

            elif self.hypernetwork[vertex].hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                # Create a new BETA, move the simplex to a partOf the new BETA
                if self.hypernetwork[vertex].hstype == hstype:
                    if self.hypernetwork[vertex]._validate_alpha_R(simplex, R, R_equal):
                        (simplex, R) = self.hypernetwork[vertex]._handle_alpha_diff_R(simplex=simplex, R=R)
                    else:
                        if self.hs_expansion:
                            (simplex, R) = self.hypernetwork[vertex]._handle_hs_expansion(simplex=simplex, R=R)
                        else:
                            raise HnRMismatch(f"{R} with Hs/vertex {vertex}.")

                if hstype == UNION_ALPHA:
                    (hstype, simplex, R) = self.hypernetwork[vertex]._handle_alpha_union(hstype=hstype,
                                                                                         simplex=simplex, R=R)

                if hstype not in [VERTEX, ANTI_VERTEX, PROPERTY] and simplex != self.hypernetwork[vertex].simplex:
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

                    if self._hypernetwork[vertex].B != B:  # TODO B
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
                if v[:4] == "@Hs_" and R_equal:
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

    def merge(self, hn, boundary_percolation=False):
        for name, hs in hn.hypernetwork.items():
            # if name in self._hypernetwork:
            #     # if self._hypernetwork[name].R.is_equal(hs.R) and self._hypernetwork[name].hstype == hs.hstype:
            #     #     B = self._hypernetwork[name].B & hs.B
            #     #     traffic = hs._union_traffic(hs.traffic)
            #     #     coloured = hs._union_coloured(hs.traffic)
            #     #
            #     # else:
            #     #     if hs.hstype in [VERTEX, PROPERTY] \
            #     #             and self._hypernetwork[name].hstype in [BETA, ALPHA, UNION_ALPHA]:
            #     #         hs = self._hypernetwork[name]
            #
            #         # else:
            #         #     subscript_1 = subscript_2 = ""
            #         #     # subscript_2 = ""
            #         #
            #         #     if hs.hstype in [BETA] \
            #         #             and self._hypernetwork[name].hstype in [ALPHA, UNION_ALPHA]:
            #         #         subscript_1 = "_A"
            #         #         subscript_2 = "_B"
            #         #     elif hs.hstype in [ALPHA, UNION_ALPHA] \
            #         #             and self._hypernetwork[name].hstype in [BETA]:
            #         #         subscript_1 = "_B"
            #         #         subscript_2 = "_A"
            #         #
            #         #     hn_hs = self._hypernetwork[name]
            #         #
            #         #     self.insert(vertex=name + "_R-" + hn_hs.R.name + subscript_1,
            #         #                 hs_class=hn_hs.hs_class, hstype=hn_hs.hstype, simplex=hn_hs.simplex,
            #         #                 R=hn_hs.R, t=hn_hs.t, C=hn_hs.C, B=hn_hs.B, N=hn_hs.N,
            #         #                 psi=hn_hs.psi, psi_inv=hn_hs.psi_inv, phi=hn_hs.phi, phi_inv=hn_hs.phi_inv,
            #         #                 traffic=hn_hs.traffic, coloured=hn_hs.coloured)
            #         #
            #         #     self.delete(name)
            #         #
            #         #     name += "_R-" + hs.R.name + subscript_2
            #
            #         B = hs.B
            #         traffic = hs.traffic
            #         coloured = hs.colouredf
            #
            # else:
            # B = hs.B
            # traffic = hs.traffic
            # coloured = hs.coloured

            try:
                self.insert(vertex=name, hs_class=hs.hs_class, hstype=hs.hstype, simplex=hs.simplex,
                            R=hs.R, t=hs.t, C=hs.C, B=hs.B, N=hs.N,
                            psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                            traffic=hs.traffic, coloured=hs.coloured, boundary_percolation=boundary_percolation)

                self._add_func_collections(hs.R, hs.psi, hs.psi_inv, hs.phi, hs.phi_inv)

            except HnRMismatch as err:
                raise HnRMismatch(err)

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

    def meet(self, hn, inc_whole_beta=True):
        def _compare(hs1, hs2):
            hstype_equal = hs1.hstype == hs1.hstype
            sigma_equal = hs1.simplex == hs2.simplex
            R_equal = hs1.R.is_equal(hs2.R)

            if hstype_equal and sigma_equal and R_equal:
                return hs1

            if hstype_equal and not sigma_equal and R_equal:
                if hs1.hstype in [ALPHA]:
                    return hs1
                if hs1.hstype in [UNION_ALPHA]:
                    return hs1
                if hs1.hstype in [BETA]:
                    return hs1

                return hs1

            if not hstype_equal and not sigma_equal and R_equal:
                if hs1.hstype in [VERTEX, PROPERTY] and hs2.hstype in [ALPHA, UNION_ALPHA, BETA]:
                    return hs2

                if (hs1.hstype in [ALPHA, UNION_ALPHA, BETA]) and hs2.hstype in [VERTEX, PROPERTY]:
                    return hs1

                if hs1.hstype in [ALPHA, UNION_ALPHA] and hs2.hstype in [BETA]:
                    return hs1

                if hs1.hstype in [BETA] and hs2.hstype in [ALPHA, UNION_ALPHA]:
                    return hs2

            return None

        new_hn = Hypernetwork()

        for name, hs in self.hypernetwork.items():
            simplex = []

            if name in hn.hypernetwork:
                passed_hs = hn.hypernetwork[name]
                new_hs = _compare(hs, passed_hs)

                if new_hs:
                    if not inc_whole_beta and hs.hstype in [BETA]:
                        for vertex in hs.simplex:
                            if vertex in hn.hypernetwork:
                                simplex.append(vertex)

                    else:
                        simplex = passed_hs.simplex

                    B = hs.B | passed_hs.B

                    new_hn.insert(hs.vertex, hs_class=hs.hs_class, hstype=hs.hstype, simplex=simplex,
                                  R=hs.R, t=hs.t, C=hs.C, B=B, psi=hs.psi, psi_inv=hs.psi_inv,
                                  phi=hs.phi, phi_inv=hs.phi_inv,
                                  traffic=hs.traffic, coloured=hs.coloured)

        self._hypernetwork.clear()

        for name, hs in new_hn.hypernetwork.items():
            self._hypernetwork.update({name: hs})

        return new_hn

    def minus(self, hn, boundary_percolation=True):
        new_hn = Hypernetwork()

        for name, hs in self.hypernetwork.items():
            try:
                if name not in hn.hypernetwork:
                    new_hn.insert(vertex=name, hs_class=hs.hs_class, hstype=hs.hstype, simplex=hs.simplex,
                                  R=hs.R, t=hs.t, C=hs.C, B=hs.B, N=hs.N,
                                  psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                                  traffic=hs.traffic, coloured=hs.coloured, boundary_percolation=boundary_percolation)

                    new_hn._add_func_collections(hs.R, hs.psi, hs.psi_inv, hs.phi, hs.phi_inv)

            except HnRMismatch as err:
                raise HnRMismatch(err)

        return new_hn

    def update(self, vertex="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None,
               N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):
        pass

    # def preparse(self, hypernet):
    #     return

    def parse(self, hypernet, boundary_percolation=True):
        class _hypersimplex:
            hs_name = ""
            hs_type = NONE
            hs_simplex = []
            hs_R = ""
            hs_t = -1
            hs_C = []
            hs_B = set()
            hs_N = "N"
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

                elif hs_k in ["V"]:
                    # _hypersimplex.hs_type = str_to_hstype(hs_k)
                    _hypersimplex.hs_simplex.append(self.parse(hs_v))

                elif hs_k in ["VERTEX", "ANTI_VERTEX", "PROPERTY"]:
                    _hypersimplex.hs_type = str_to_hstype(hs_k)
                    _hypersimplex.hs_name = hs_v[0]["V"]
                    _hypersimplex.hs_N = hs_v[1]["N"]

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

        for hn in hypernet:
            if isinstance(hn, dict):
                _parse_hs(hn)

            else:
                for hs in hn:
                    _parse_hs(hs)

            if _hypersimplex.hs_type != NONE:
                try:
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
                                       coloured=None,
                                       boundary_percolation=boundary_percolation)

                except HnRMismatch as err:
                    raise HnRMismatch(err)

                if _relation.hs_where:
                    self.relations[_relation.hs_R] = _relation.hs_where

                _clear()

            else:
                if _relation.hs_where:
                    self.relations[_relation.hs_R] = _relation.hs_where[0] \
                        if len(_relation.hs_where) == 1 else _relation.hs_where

        return name

    def search(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="N", partOf=None):
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
                if hstype in [VERTEX, ANTI_VERTEX, PROPERTY]:
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

    def get_subHn(self, vertex="", hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="N", partOf=None):
        class temp:
            Hn = None

        def _get_subHn(_hs):
            if _hs.hstype not in [VERTEX, ANTI_VERTEX, PROPERTY]:
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

            elif self._hypernetwork[_vertex].hstype in [VERTEX, ANTI_VERTEX, PROPERTY]:
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
            if hs.hstype not in [NONE, VERTEX, ANTI_VERTEX, PROPERTY]:
                res = res + str(hs) + "\n"

        return res

    def add_to_boundary(self, boundary, boundary_percolation=True, vertices=[]):
        def percolate_boundary(*_vertices):
            for v in _vertices:
                self._hypernetwork[v].B.add(boundary)
                percolate_boundary(self._hypernetwork[v].simplex)

        for vertex in vertices:
            self._hypernetwork[vertex].B.add(boundary)

            if boundary_percolation:
                percolate_boundary(self._hypernetwork[vertex].simplex)

    def remove_from_boundary(self, boundary, boundary_percolation=True, *vertices):
        def _next(next_hs):
            for name in self._hypernetwork[next_hs].simplex:
                _next(name)

            self._hypernetwork[next_hs].remove_from_boundary(boundary)

            if vertex not in self._boundary_exclusions:
                self._boundary_exclusions.update({vertex: set()})

            self._boundary_exclusions[vertex].add(boundary)

        for vertex in vertices:
            if boundary_percolation:
                if vertex in self._hypernetwork:
                    _next(vertex)
            else:
                self._hypernetwork[vertex].remove_from_boundary(boundary)

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

            elif simplex.hstype in [VERTEX, ANTI_VERTEX, PROPERTY]:
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
