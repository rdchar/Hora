import copy
import logging
import re
from pprint import pprint

from networkx import intersection

from hypernetworks.core.HTConfig import hs_override_hs_type
from hypernetworks.core.HTErrors import HnVertexNoFound, HnUnknownHsType, HnInsertError, HnRMismatch, HnHsNotExistInHn
from hypernetworks.core.HTTypes import Types
from hypernetworks.core.Hypersimplex import NONE, ALPHA, BETA, VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY, \
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

    def _create_hs(self, _hn, vertex, named="", hs_class=HS_STANDARD, hstype=VERTEX, simplex=None,
                   R="", t=-1, C=None, B=None, N="N",
                   psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):

        # TODO this should be injected at start of application.
        if hs_class == HS_HYPER_PN:
            from hyperPn.core.hyperPn import HPnHypersimplex
            return HPnHypersimplex(self, vertex=vertex, named=named, hs_class=hs_class, hstype=hstype, simplex=simplex,
                                   R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                   partOf=partOf, traffic=traffic, coloured=coloured)

        if hs_class == HS_ACTIVITY:
            from core.ActivityHn import ActivityHypersimplex
            return ActivityHypersimplex(self, vertex=vertex, named=named, hs_class=hs_class, hstype=hstype, simplex=simplex,
                                        R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                        partOf=partOf, traffic=traffic, coloured=coloured)

        return Hypersimplex(self, vertex=vertex, named=named, hstype=hstype, simplex=simplex, R=R, t=t, C=C, B=B, N=N,
                            psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                            partOf=partOf, traffic=traffic, coloured=coloured)

    def change_hs_class(self, hs_name, new_hs_class):
        if hs_name not in self._hypernetwork:
            raise HnHsNotExistInHn

        hs = self._hypernetwork[hs_name]
        if new_hs_class == HS_HYPER_PN:
            from hyperPn.core.hyperPn import HPnHypersimplex
            new_hs = HPnHypersimplex(self, vertex=hs.vertex, named=hs.named, hs_class=new_hs_class, hstype=hs.hstype,
                                     simplex=hs.simplex, R=hs.R, t=hs.t, C=hs.C, B=hs.B, N=hs.N,
                                     psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                                     partOf=hs.partOf, traffic=hs.traffic, coloured=hs.coloured)

            del self._hypernetwork[hs_name]
            self._hypernetwork[hs_name] = new_hs

        if new_hs_class == HS_ACTIVITY:
            from core.ActivityHn import ActivityHypersimplex
            new_hs = ActivityHypersimplex(self, vertex=hs.vertex, named=hs.named, hs_class=new_hs_class, hstype=hs.hstype,
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

    def _add(self, vertex, named="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="N",
             psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):
        if vertex in self._hypernetwork:
            # Update an existing node
            temp = self._hypernetwork[vertex]

            if temp.named and not named:
                named = temp.named

            if temp.hstype not in [NONE, VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY] and not hs_override_hs_type:
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

            if temp.hstype == ANTI_PROPERTY:
                # TODO not sure it is correct
                hstype = temp.hstype

            if temp.hstype == ANTI_VERTEX:
                # TODO not sure it is correct
                hstype = temp.hstype

            temp.update(hstype=hstype, named=named, simplex=simplex, R=R, t=t, C=C, B=B, N=N,
                        psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                        partOf=partOf, traffic=traffic, coloured=coloured)

            self._hypernetwork[vertex] = temp

            if hs_class != self._hypernetwork[vertex].hs_class:
                self.change_hs_class(vertex, hs_class)

        else:
            hs = self._create_hs(self, vertex=vertex, named=named, hs_class=hs_class, hstype=hstype, simplex=simplex,
                                 R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                 partOf=partOf, traffic=traffic, coloured=coloured)

            self._hypernetwork.update({vertex: hs})

        self._add_func_collections(R, psi, psi_inv, phi, phi_inv)

    def insert_hs(self, vertex="", hs=None, boundary_percolation=True):
        if vertex:
            vertex = hs.vertex

        self.insert(vertex, hstype=hs.hstype, simplex=hs.simplex, R=hs.R, t=hs.t, C=hs.C, B=hs.B,
                    N=hs.N, psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
                    traffic=hs.traffic, coloured=hs.coloured, boundary_percolation=boundary_percolation)

    # def delete(self, vertex="", R="", del_children=False, B=""):
    #     def _delete_vertex(_vertex):
    #         for _vert in self._hypernetwork[_vertex].simplex:
    #             if _vert in self._hypernetwork:
    #                 if _vertex in self._hypernetwork[_vert].partOf:
    #                     self._hypernetwork[_vert].partOf.remove(_vertex)

    #             if del_children:
    #                 _delete_vertex(_vert)

    #         # Removes all instances of the vertex.
    #         for _whole in self._hypernetwork[_vertex].partOf:
    #             for temp in self._hypernetwork[_whole].simplex:
    #                 _part = remove_special(temp)
    #                 if _part == _vertex:
    #                     self._hypernetwork[_whole].simplex.remove(temp)

    #         del self._hypernetwork[_vertex]

    #     # End _delete_vertex

    #     def _delete_whole_boundary():
    #         temp = copy.deepcopy(self._hypernetwork)
    #         peaks = []

    #         for name, hs in temp.items():
    #             if B in hs.B:
    #                 for parent in hs.partOf:
    #                     if parent in self._hypernetwork:
    #                         if len(hs.B) <= 1 and name in self._hypernetwork[parent].simplex:
    #                             self._hypernetwork[parent].simplex.remove(name)

    #                 if len(hs.B) == 1:
    #                     if name in self._hypernetwork:
    #                         del self._hypernetwork[name]

    #                 else:
    #                     self._hypernetwork[name].B.remove(B)

    #         return peaks

    #     # End _delete_whole_boundary

    #     def _delete_boundary():
    #         def _delete_vertex_from_boundary(_vertex, _parent):
    #             if _vertex in self._hypernetwork:
    #                 hs = self._hypernetwork[_vertex]

    #                 if B in hs.B:
    #                     if len(hs.B) == 1 and len(hs.partOf) == 1:
    #                         del self._hypernetwork[_vertex]

    #                     else:
    #                         if len(self._hypernetwork[_vertex].partOf) == 1:
    #                             self._hypernetwork[_vertex].B.remove(B)

    #                 else:
    #                     parents = set()
    #                     for parent in hs.partOf:
    #                         if parent in self._hypernetwork:
    #                             if B in self._hypernetwork[parent].B and len(self._hypernetwork[parent].B) == 1:
    #                                 parents.add(parent)

    #                     self._hypernetwork[_vertex].partOf = self._hypernetwork[_vertex].partOf.difference(parents)

    #         # End delete_from_boundary

    #         def _delete_from_boundary(_vertex, _parent):
    #             if _vertex in self._hypernetwork:
    #                 for vert in self._hypernetwork[_vertex].simplex:
    #                     hs = self._hypernetwork[vert]

    #                     if B in hs.B:
    #                         _delete_from_boundary(vert, _vertex)

    #                     _delete_vertex_from_boundary(vert, _vertex)

    #                 for vert in self._hypernetwork[_vertex].simplex:
    #                     if vert not in self._hypernetwork:
    #                         self._hypernetwork[_vertex].simplex.remove(vert)

    #         # End _delete_from_boundary

    #         peaks = self._hypernetwork[vertex].partOf

    #         for peak in peaks:
    #             _delete_from_boundary(vertex, peak)

    #             if vertex in self._hypernetwork[peak].simplex:
    #                 self._hypernetwork[peak].simplex.remove(vertex)

    #             if vertex in self._hypernetwork:
    #                 if B in self._hypernetwork[vertex].B:
    #                     if len(self._hypernetwork[vertex].B) == 1:
    #                         del self._hypernetwork[vertex]
    #                     else:
    #                         self._hypernetwork[vertex].B.remove(B)

    #     # End _delete_boundary

    #     # TODO may need more work
    #     if R:
    #         vertices = self.search(R=R)
    #         for vert in vertices:
    #             _delete_vertex(_vertex=vert)

    #     elif B:
    #         if vertex and vertex in self._hypernetwork:
    #             _delete_boundary()
    #         else:
    #             _delete_whole_boundary()

    #     elif vertex and vertex in self._hypernetwork:
    #         _delete_vertex(_vertex=vertex)

    #     else:
    #         raise HnVertexNoFound

    def minus(self, vertex=None, R=None, B=None, del_children=False, boundary_percolation=True):
        """
        Paper 3 'minus' semantics:
        - Scope can be: (a) a specific vertex/hypersimplex name; (b) all items with relation R; (c) a boundary tag B.
        - Remove selected items and detach references from parents (reciprocal cleanup).
        - Prune invalid leftovers: empty β -> drop; α with role loss/arity break -> drop; orphan atoms allowed but parents cleaned.
        - Boundary-scoped: only effects within B; for multi-tagged items, remove tag B (and delete only if B was sole tag and the item becomes unreachable).
        - Deterministic and all-or-nothing: operate on a copy; commit if successful; enforce axioms/conditions at end.
        """
        import copy

        H = copy.deepcopy(self._hypernetwork)

        def _prune_invalid(name):
            """Drop empty β; drop α if its arity is broken (role removed) or becomes empty; tidy atoms with no parents."""
            if name not in H:
                return
            hs = H[name]
            # β must have >= 1 participant
            if hs.hstype == BETA and len(hs.simplex) == 0:
                _delete_node(name)
                return
            # α must preserve role order and arity; if any child missing, arity is broken
            if hs.hstype in [ALPHA, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
                if any(v not in H for v in hs.simplex):
                    _delete_node(name)
                    return
                if len(hs.simplex) == 0:
                    _delete_node(name)
                    return

        def _detach_from_parents(child):
            """Remove child from each parent's simplex and drop parents that become invalid."""
            if child not in H:
                return
            for p in list(H[child].partOf):
                if p in H:
                    # Remove all occurrences safely
                    H[p].simplex = [x for x in H[p].simplex if remove_special(x) != child]
                    if child in H[p].partOf:
                        H[child].partOf.discard(p)
                    _prune_invalid(p)

        def _delete_node(name):
            """Delete node and detach from parents; optionally cascade to children if del_children."""
            if name not in H:
                return
            # Optionally cascade down first (children)
            if del_children:
                for c in list(H[name].simplex):
                    c0 = remove_special(c)
                    if c0 in H:
                        _delete_node(c0)
            # Detach upward
            _detach_from_parents(name)
            # Finally delete this node
            if name in H:
                del H[name]

        def _scope_names_by_R(Rq):
            out = set()
            for nm, hs in H.items():
                try:
                    if hs.R and (hs.R.is_equal(Rq) if hasattr(hs.R, "is_equal") else hs.R == Rq):
                        out.add(nm)
                except Exception:
                    pass
            return out

        def _scope_names_by_boundary(Bq):
            """Only act within boundary Bq. If an item has {Bq} -> delete; if it has Bq ∪ others -> remove Bq tag; detach edges that exist only via parents in {Bq}."""
            return {nm for nm, hs in H.items() if isinstance(hs.B, set) and Bq in hs.B}

        # ---- Compute deletion set deterministically
        to_delete = set()
        tag_removals = {}  # name -> remove tag B

        if vertex:
            if vertex in H:
                to_delete.add(vertex)

        elif R:
            to_delete |= _scope_names_by_R(R)

        elif B:
            candidates = _scope_names_by_boundary(B)
            # Boundary-scoped policy:
            #  - If hs.B == {B} -> delete the item.
            #  - If B in hs.B and |hs.B| > 1 -> just remove B tag.
            for nm in candidates:
                hs = H[nm]
                if len(hs.B) == 1:
                    to_delete.add(nm)
                else:
                    tag_removals.setdefault(nm, set()).add(B)
        else:
            raise HnVertexNoFound  # no scope provided

        # ---- Apply tag removals first (boundary-scoped soften)
        for nm, tags in sorted(tag_removals.items()):
            if nm in H:
                H[nm].B = set(H[nm].B) - set(tags)

        # ---- Delete targets (and clean reciprocal links)
        for nm in sorted(to_delete):
            _delete_node(nm)

        # ---- Post-pass: prune any parents that became invalid (empty β, broken α)
        # Iterate until fixed-point
        changed = True
        while changed:
            changed = False
            for nm in list(H.keys()):
                before = len(H)
                _prune_invalid(nm)
                if len(H) != before:
                    changed = True
                    break

        # ---- Commit (all-or-nothing) and enforce axioms/conditions
        self._hypernetwork.clear()
        for nm, hs in H.items():
            self._hypernetwork[nm] = hs

        if hasattr(self, "_enforce_axioms_and_conditions"):
            self._enforce_axioms_and_conditions()

        return self

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

    def insert(self, vertex="", named="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None,
               N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None,
               boundary_exclusions=None, boundary_percolation=True):

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
            self._add(vertex=vertex, named=named, hs_class=hs_class, hstype=hstype, simplex=simplex,
                      R=R, t=t, C=C, B=B, N=N,
                      psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                      partOf=partOf if isinstance(partOf, set) else {partOf}, traffic=traffic, coloured=coloured)

            for i, v in enumerate(simplex):
                if "PROPERTY" in v:
                    self._hypernetwork[vertex].simplex[i] = v["PROPERTY"]
                if "ANTI_PROPERTY" in v:
                    self._hypernetwork[vertex].simplex[i] = v["ANTI_PROPERTY"]
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
                        self._add(vertex=v["PROPERTY"], named=named, hs_class=hs_class, hstype=PROPERTY, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)
                    if "ANTI_PROPERTY" in v:
                        self._add(vertex=v["ANTI_PROPERTY"], named=named, hs_class=hs_class, hstype=ANTI_PROPERTY, partOf={vertex},
                                  B=child_B,
                                  traffic=traffic, coloured=coloured)
                    elif "ANTI_VERTEX" in v:
                        self._add(vertex=v["ANTI_VERTEX"], named=named, hs_class=hs_class, hstype=ANTI_VERTEX, partOf={vertex},
                                  B=child_B,
                                  traffic=traffic, coloured=coloured)
                    else:
                        key = list(v.keys())[0]
                        self._add(vertex=v[key], named=named, hs_class=hs_class, hstype=VERTEX, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)

                else:
                    if hstype:
                        self._add(vertex=v, named=named, hs_class=hs_class, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)

                    else:
                        self._add(vertex=v, named=named, hs_class=hs_class, hstype=VERTEX, partOf={vertex}, B=child_B,
                                  traffic=traffic, coloured=coloured)

        # End _insert

        if simplex is None:
            simplex = []

        if partOf is None:
            partOf = set()

        R_equal = True
        do_search = True

        if hstype in [PROPERTY, ANTI_PROPERTY]:
            if vertex in self.hypernetwork:
                self._hypernetwork[vertex].update(vertex=vertex, named=named, hstype=hstype, R=R, t=t, C=C, B=B, N=N,
                                                  psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                                  traffic=traffic, coloured=coloured)

            else:
                self._add(vertex=vertex, named=named, hs_class=hs_class, hstype=hstype, simplex=simplex,
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

                elif hstype in [ALPHA, VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY, UNION_ALPHA, IMMUTABLE_ALPHA, SEQUENCE]:
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

                if hstype not in [VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY] and simplex != self.hypernetwork[vertex].simplex:
                    vertex = self.hypernetwork[vertex]._handle_Hs_union_dups(hstype=hstype, simplex=simplex,
                                                                             R=R, t=t, C=C, B=B, N=N,
                                                                             psi=psi, psi_inv=psi_inv,
                                                                             phi=phi, phi_inv=phi_inv,
                                                                             partOf=partOf, traffic=traffic,
                                                                             coloured=coloured, dup=True)
                    do_search = False

                else:
                    if R:
                        if not self._hypernetwork[vertex].R.is_equal(R):
                            R = self._hypernetwork[vertex].R

                    if self._hypernetwork[vertex].B != B:  # TODO B
                        if B:
                            if boundary_percolation:
                                B = self._hypernetwork[vertex].B.union(B)
                            else:
                                B = self._hypernetwork[vertex].B

                    partOf.add(vertex)
            elif self.hypernetwork[vertex].hstype in [PROPERTY, ANTI_PROPERTY]:
                self._hypernetwork[vertex].update(vertex=vertex, named=named, hstype=hstype, hs_class=hs_class,
                                                  R=R, t=t, C=C, B=B, N=N,
                                                  psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                                  traffic=traffic, coloured=coloured)
                
            elif self._hypernetwork[vertex].hstype in [VERTEX] and hstype in [ALPHA, UNION_ALPHA, BETA]:
                self._hypernetwork[vertex].update(vertex=vertex, named=named, hstype=hstype, hs_class=hs_class, simplex=simplex,
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
                if hstype not in [PROPERTY, ANTI_PROPERTY]:
                    search = self.search(hstype=hstype, vertex=vertex)

        if vertex == "" or not vertex:
            if hstype not in [PROPERTY, ANTI_PROPERTY]:
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

                self._hypernetwork[vertex].update(vertex=vertex, named=named, R=R, t=t, C=C, B=B, N=N,
                                                  psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                                  traffic=traffic, coloured=coloured)

        else:
            # TODO added this to union the partOf, not sure if it is correct, needs testing
            if hstype not in [PROPERTY, ANTI_PROPERTY]:
                _insert(partOf, hs_class=hs_class)  # TODO this is new and not fully tested

        for v in simplex:
            if isinstance(v, dict):
                key = list(v.keys())[0]
                v = v[key]

            if v in self._hypernetwork:
                self._hypernetwork[v].partOf.add(vertex)
            else:
                self.insert(v, hstype=VERTEX, partOf={vertex}, B=set() if boundary_percolation else "B")

        # Remove cyclic references
        # _remove_cyclic()
        if not boundary_exclusions:
            boundary_exclusions = self._boundary_exclusions

        self.apply_boundary_exclusions(boundary_exclusions)

        return vertex

    def merge(self, hn, boundary_percolation=True):
        for name, hs in hn.hypernetwork.items():
            try:
                self.insert(vertex=name, named=hs.named, hs_class=hs.hs_class, hstype=hs.hstype, simplex=hs.simplex,
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

    # def meet(self, hn, inc_whole_beta=True, boundary_percolation=True):
    #     def _compare(hs1, hs2):
    #         hstype_equal = hs1.hstype == hs2.hstype
    #         sigma_equal = hs1.simplex == hs2.simplex
    #         R_equal = hs1.R.is_equal(hs2.R)

    #         if hs1.hstype in [VERTEX] and hs2.hstype not in [VERTEX]:
    #             return hs2

    #         if hs2.hstype in [VERTEX] and hs1.hstype not in [VERTEX]:
    #             return hs1

    #         if hstype_equal and sigma_equal and R_equal:
    #             return hs1

    #         if hstype_equal and not sigma_equal and R_equal:
    #             if hs1.hstype in [ALPHA]:
    #                 return hs1
    #             if hs1.hstype in [UNION_ALPHA]:
    #                 return hs1
    #             if hs1.hstype in [BETA]:
    #                 return hs1

    #             return hs1
            
    #         if not hstype_equal and not sigma_equal and R_equal:
    #             if hs1.hstype in [VERTEX, PROPERTY, ANTI_PROPERTY] and hs2.hstype in [ALPHA, UNION_ALPHA, BETA]:
    #                 return hs2

    #             if (hs1.hstype in [ALPHA, UNION_ALPHA, BETA]) and hs2.hstype in [VERTEX, PROPERTY, ANTI_PROPERTY]:
    #                 return hs1

    #             if hs1.hstype in [ALPHA, UNION_ALPHA] and hs2.hstype in [BETA]:
    #                 return hs1

    #             if hs1.hstype in [BETA] and hs2.hstype in [ALPHA, UNION_ALPHA]:
    #                 return hs2

    #         return None

    #     new_hn = Hypernetwork()

    #     for name, hs in self.hypernetwork.items():
    #         simplex = []

    #         if name in hn.hypernetwork:
    #             passed_hs = hn.hypernetwork[name]
    #             new_hs = _compare(hs, passed_hs)

    #             if new_hs:
    #                 if not inc_whole_beta and hs.hstype in [BETA]:
    #                     for vertex in hs.simplex:
    #                         if vertex in hn.hypernetwork:
    #                             simplex.append(vertex)

    #                 else:
    #                     simplex = new_hs.simplex

    #                 B = hs.B | new_hs.B

    #                 new_hn.insert(hs.vertex, named=hs.named, hs_class=hs.hs_class, hstype=hs.hstype, simplex=simplex,
    #                               R=hs.R, t=hs.t, C=hs.C, B=B, psi=hs.psi, psi_inv=hs.psi_inv,
    #                               phi=hs.phi, phi_inv=hs.phi_inv,
    #                               traffic=hs.traffic, coloured=hs.coloured, 
    #                               boundary_percolation=boundary_percolation)

    #     self._hypernetwork.clear()

    #     for name, hs in new_hn.hypernetwork.items():
    #         self._hypernetwork.update({name: hs})

    #     return new_hn

    def meet(self, hn, inc_whole_beta: bool = False, boundary_percolation: bool = True):
        """
        Meet (Paper 3 semantics):
        - Same-name only; R must match to proceed (atomics exempt).
        - α / UNION_ALPHA: role-wise intersection at aligned positions; unequal arity ⇒ no meet.
        - β:
            * inc_whole_beta == False (default): shrink to participant intersection; drop if empty.
            * inc_whole_beta == True: if there is any overlap, keep the full left β (do not shrink).
        - Atomics (VERTEX / PROPERTY / ANTI_PROPERTY): keep only if identical on both sides.
        - Boundaries: intersection (coerced to sets).
        - Deterministic: iterate names in sorted order; sort any set-derived lists.
        """

        def _as_set(x):
            if x is None:
                return set()
            if isinstance(x, set):
                return set(x)
            if isinstance(x, (list, tuple)):
                return set(x)
            return {x} if x != "" else set()

        def _B_meet(b1, b2):
            return _as_set(b1) & _as_set(b2)

        def _R_equal(r1, r2):
            # R may be objects (with is_equal) or strings/None
            if hasattr(r1, "is_equal"):
                try:
                    return r1.is_equal(r2)
                except Exception:
                    return False
            if hasattr(r2, "is_equal"):
                try:
                    return r2.is_equal(r1)
                except Exception:
                    return False
            return r1 == r2

        def _alpha_meet(s1, s2):
            if len(s1) != len(s2):
                return []  # unequal arity ⇒ no aligned roles
            return [a for (a, b) in zip(s1, s2) if a == b]

        def _beta_inter(s1, s2):
            return sorted(set(s1) & set(s2))

        new_hn = Hypernetwork()

        for name in sorted(self.hypernetwork.keys()):
            hs1 = self.hypernetwork[name]
            hs2 = hn.hypernetwork.get(name)
            if hs2 is None:
                continue

            t1, t2 = hs1.hstype, hs2.hstype

            # R must match to proceed (except for atomics)
            r_ok = _R_equal(hs1.R, hs2.R)
            if not r_ok and not (t1 in [VERTEX, PROPERTY, ANTI_PROPERTY] and t2 in [VERTEX, PROPERTY, ANTI_PROPERTY]):
                continue

            # α / UNION_ALPHA with α / UNION_ALPHA → role-wise intersection
            if t1 in [ALPHA, UNION_ALPHA] and t2 in [ALPHA, UNION_ALPHA]:
                inter = _alpha_meet(hs1.simplex, hs2.simplex)
                if not inter:
                    continue
                B = _B_meet(hs1.B, hs2.B)
                new_hn.insert(
                    hs1.vertex,
                    named=hs1.named,
                    hs_class=hs1.hs_class,
                    hstype=t1,  # keep left flavour
                    simplex=inter,
                    R=hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                    psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                    traffic=hs1.traffic, coloured=hs1.coloured,
                    boundary_percolation=boundary_percolation
                )
                if hasattr(new_hn, "_add_func_collections"):
                    new_hn._add_func_collections(hs1.R, hs1.psi, hs1.psi_inv, hs1.phi, hs1.phi_inv)
                continue

            # β with β
            if t1 == BETA and t2 == BETA:
                inter = _beta_inter(hs1.simplex, hs2.simplex)
                if not inter:
                    continue
                B = _B_meet(hs1.B, hs2.B)
                out_simplex = hs1.simplex if inc_whole_beta else inter
                # If strict mode and intersection is empty, we already continued; otherwise insert:
                new_hn.insert(
                    hs1.vertex,
                    named=hs1.named,
                    hs_class=hs1.hs_class,
                    hstype=BETA,
                    simplex=out_simplex,
                    R=hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                    psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                    traffic=hs1.traffic, coloured=hs1.coloured,
                    boundary_percolation=boundary_percolation
                )
                if hasattr(new_hn, "_add_func_collections"):
                    new_hn._add_func_collections(hs1.R, hs1.psi, hs1.psi_inv, hs1.phi, hs1.phi_inv)
                continue

            # Atomics (exact match only)
            if t1 in [VERTEX, PROPERTY, ANTI_PROPERTY] and t2 in [VERTEX, PROPERTY, ANTI_PROPERTY]:
                if t1 == t2 and hs1.vertex == hs2.vertex:
                    B = _B_meet(hs1.B, hs2.B)
                    new_hn.insert(
                        hs1.vertex,
                        named=hs1.named,
                        hs_class=hs1.hs_class,
                        hstype=t1,
                        simplex=[],
                        R="", t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                        psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                        traffic=hs1.traffic, coloured=hs1.coloured,
                        boundary_percolation=boundary_percolation
                    )
                continue

            # Mixed types: drop by default
            continue

        # Atomic swap for all-or-nothing semantics
        self._hypernetwork.clear()
        for k, v in new_hn.hypernetwork.items():
            self._hypernetwork[k] = v

        if hasattr(self, "_enforce_axioms_and_conditions"):
            self._enforce_axioms_and_conditions()

        return new_hn

    # def difference(self, hn, boundary_percolation=True, ignore_boundary=False):
    #     new_hn = Hypernetwork()

    #     for name, hs in self.hypernetwork.items():
    #         try:
    #             if name not in hn.hypernetwork:
    #                 new_hn.insert(vertex=name, named=hs.named, hs_class=hs.hs_class, hstype=hs.hstype, simplex=hs.simplex,
    #                               R=hs.R, t=hs.t, C=hs.C, B=hs.B, N=hs.N,
    #                               psi=hs.psi, psi_inv=hs.psi_inv, phi=hs.phi, phi_inv=hs.phi_inv,
    #                               traffic=hs.traffic, coloured=hs.coloured, boundary_percolation=boundary_percolation)

    #                 new_hn._add_func_collections(hs.R, hs.psi, hs.psi_inv, hs.phi, hs.phi_inv)

    #         except HnRMismatch as err:
    #             raise HnRMismatch(err)

    #     return new_hn

    def difference(self, hn, boundary_percolation=True, ignore_boundary=False):
        """
        Paper 3 semantics for H1 \ H2:
        - Only compare hypersimplices with the same name.
        - If name not in H2 -> copy hs from H1.
        - If name in H2 but R or type differ -> keep hs from H1 unchanged (incompatible -> retained).
        - If R and type match:
            * α / UNION_ALPHA: role-wise subtraction (remove positions where roles match exactly and in order).
                If nothing remains, drop.
            * β: set subtraction of participants (left \ right). If empty, drop.
            * VERTEX / PROPERTY / ANTI_PROPERTY: if exactly the same atomic, drop; else keep left.
        - Boundaries: if ignore_boundary=True keep left B; else compute left-minus-right tags as conservative default.
        - Determinism: iterate in a fixed order; sort any set-derived lists.
        """
        def _R_equal(r1, r2):
            try:
                return r1.is_equal(r2)
            except AttributeError:
                return r1 == r2

        def _alpha_subtract(s1, s2):
            # Only positions that do NOT match exactly are retained; arity must match to compare strictly.
            if len(s1) != len(s2):
                # Types match but arity differs: treat as incompatible → retain left as-is.
                return None  # signal "incompatible"
            return [a for (a, b) in zip(s1, s2) if a != b]

        def _beta_subtract(s1, s2):
            return sorted(set(s1) - set(s2))

        new_hn = Hypernetwork()

        for name in sorted(self.hypernetwork.keys()):
            hs1 = self.hypernetwork[name]
            hs2 = hn.hypernetwork.get(name)

            # Case 1: name not in H2 → copy from H1
            if hs2 is None:
                new_hn.insert(
                    vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=hs1.hstype, simplex=list(hs1.simplex),
                    R=hs1.R, t=hs1.t, C=hs1.C, B=set(hs1.B) if isinstance(hs1.B, set) else hs1.B, N=hs1.N,
                    psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                    traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                )
                continue

            # Case 2: name in H2 but R/type differ → retain hs1 unchanged
            if not _R_equal(hs1.R, hs2.R) or hs1.hstype != hs2.hstype:
                new_hn.insert(
                    vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=hs1.hstype, simplex=list(hs1.simplex),
                    R=hs1.R, t=hs1.t, C=hs1.C, B=set(hs1.B) if isinstance(hs1.B, set) else hs1.B, N=hs1.N,
                    psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                    traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                )
                continue

            # Case 3: R and type match → subtract contents by type
            t = hs1.hstype

            # Boundary policy
            if ignore_boundary:
                B = hs1.B
            else:
                try:
                    B = (hs1.B - hs2.B)
                except TypeError:
                    # If B is not a set-like, fall back to left B
                    B = hs1.B

            if t in [ALPHA, UNION_ALPHA]:
                sub = _alpha_subtract(hs1.simplex, hs2.simplex)
                if sub is None:
                    # Incompatible arity under same type/R → retain left unchanged
                    new_hn.insert(
                        vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=t, simplex=list(hs1.simplex),
                        R=hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                        psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                        traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                    )
                elif sub:
                    new_hn.insert(
                        vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=t, simplex=sub,
                        R=hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                        psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                        traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                    )
                # else: sub is empty → drop

            elif t == BETA:
                sub = _beta_subtract(hs1.simplex, hs2.simplex)
                if sub:
                    new_hn.insert(
                        vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=BETA, simplex=sub,
                        R=hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                        psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                        traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                    )
                # else: empty → drop

            elif t in [VERTEX, PROPERTY, ANTI_PROPERTY]:
                # If identical atomic on both sides → remove; else keep left
                if not (hs1.vertex == hs2.vertex and t == hs2.hstype):
                    new_hn.insert(
                        vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=t, simplex=[],
                        R="" if t in [VERTEX, PROPERTY, ANTI_PROPERTY] else hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                        psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                        traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                    )
            else:
                # Unknown/extended types → conservative: retain left as-is
                new_hn.insert(
                    vertex=name, named=hs1.named, hs_class=hs1.hs_class, hstype=t, simplex=list(hs1.simplex),
                    R=hs1.R, t=hs1.t, C=hs1.C, B=B, N=hs1.N,
                    psi=hs1.psi, psi_inv=hs1.psi_inv, phi=hs1.phi, phi_inv=hs1.phi_inv,
                    traffic=hs1.traffic, coloured=hs1.coloured, boundary_percolation=boundary_percolation
                )

        # Atomic swap for all-or-nothing semantics
        self._hypernetwork.clear()
        for k, v in new_hn.hypernetwork.items():
            self._hypernetwork[k] = v

        if hasattr(self, "_enforce_axioms_and_conditions"):
            self._enforce_axioms_and_conditions()

        return new_hn

    def update(self, vertex="", nameed="", hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None,
               N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):
        pass

    # def preparse(self, hypernet):
    #     return

    def parse(self, hypernet, boundary_percolation=True):
        class _hypersimplex:
            hs_name = ""
            hs_named = ""
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

                elif hs_k in ["PROPERTY", "ANTI_PROPERTY"]:
                    _hypersimplex.hs_type = str_to_hstype(hs_k)
                    _hypersimplex.hs_name = hs_v
                    _hypersimplex.hs_N = "N"

                elif hs_k in ["VERTEX", "ANTI_VERTEX"]:
                    _hypersimplex.hs_type = str_to_hstype(hs_k)
                    _hypersimplex.hs_name = hs_v[0]["V"]

                    if any("NAME" in d for d in hs_v):
                        _hypersimplex.hs_named = hs_v[1]["NAME"]
                    else:
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
            _hypersimplex.hs_named = ""
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
                                       named=_hypersimplex.hs_named,
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
                if hstype in [VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY]:
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
            if _hs.hstype not in [VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY]:
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

            elif self._hypernetwork[_vertex].hstype in [VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY]:
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
            if hs.hstype not in [NONE, VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY]:
                res = res + str(hs) + "\n"

        return res

    def add_to_boundary(self, boundary, boundary_percolation=False, vertices=[]):
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

            elif simplex.hstype in [VERTEX, ANTI_VERTEX, PROPERTY, ANTI_PROPERTY]:
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
