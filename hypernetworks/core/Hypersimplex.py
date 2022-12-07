# Relation Types
import copy

from hypernetworks.core.HTConfig import hs_default_N

HS_STANDARD = 0
HS_HYPER_PN = 1
HS_ACTIVITY = 2

R_BASIC = 0
LOGIC = 1
ANN = 2
LAMBDA = 3
R_TRANSITION = 4

# Node type
NONE = -1
VERTEX = 0
ALPHA = 1
BETA = 2
PROPERTY = 3
UNION_ALPHA = 4
IMMUTABLE_ALPHA = 5
SEQUENCE = 6

# Special types
NONE = -1
UNION = 1
IMMUTABLE = 2

HS_TYPE = ['NONE', 'VERTEX', 'ALPHA', 'BETA', 'PROPERTY', 'UNION_ALPHA', 'IMMUTABLE_ALPHA', 'SEQUENCE']
hstype_to_str = lambda x: HS_TYPE[x + 1]
str_to_hstype = lambda x: HS_TYPE.index(x) - 1

SPECIAL_TYPE = ['NONE', 'UNION', 'IMMUTABLE']
special_to_str = lambda x: SPECIAL_TYPE[x + 1]
str_to_special = lambda x: SPECIAL_TYPE.index(x) - 1


# is_sequence = lambda vertex: vertex[:4] in ["SEQ@"]
# is_immutable = lambda vertex: vertex[:4] in ["IMM@"]
# strip_special = lambda vertex: vertex[4:] if vertex[:4] in ["SEQ@", "IMM@"] else vertex


class HsRelation:
    # def __init__(self, name, reltype=BASIC, content=None):
    def __init__(self, name, reltype=R_BASIC):
        self._name = name
        # self._content = "" if content else content
        self._reltype = reltype

    def _updateR(self, R):
        return HsRelation(R, reltype=R_BASIC) if isinstance(R, str) else R

    @property
    def reltype(self):
        return self._reltype

    @reltype.setter
    def reltype(self, value):
        self._reltype = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def is_equal(self, value):
        if value == ' ':
            return self._name == value

        return self._name == value._name


class HsVertex:
    def __init__(self, _vertex, _type=""):
        self._vertex = _vertex
        self._type = _type

    @property
    def vertex(self):
        return self._vertex

    @vertex.setter
    def vertex(self, _vertex):
        self._vertex = _vertex

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, _type):
        self._type = _type


class Hypersimplex:
    def __init__(self, _hn, vertex, hs_class=HS_STANDARD, hstype=VERTEX, simplex=None, R="", t=-1, C=None,
                 B=None, N="N", psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):

        self._hypernetwork = _hn
        self._hs_class = hs_class
        self._simplex = []
        self._special = None

        if hstype == IMMUTABLE_ALPHA:
            hstype = ALPHA
            self._special = IMMUTABLE
        else:
            self._special = NONE

        self._vertex = HsVertex(vertex)

        if simplex:
            for v in simplex:
                self._simplex.append(v)

        self._partOf = set() if partOf is None else partOf.copy()
        self._hstype = VERTEX if hstype == NONE else hstype
        self._R = HsRelation(R, reltype=R_BASIC) if isinstance(R, str) else R
        self._t = t
        self._C = [] if C is None else C
        self._B = set() if B is None else B.copy()
        self._other = []
        self._N = "N" if hs_default_N and not N else N
        self._psi = psi
        self._psi_inv = psi_inv
        self._phi = phi
        self._phi_inv = phi_inv
        self._traffic = traffic
        self._coloured = coloured

    def _traffic_upsert(self, existing, new):
        return new

    def _coloured_upsert(self, existing, new):
        return new

    def _union_coloured(self, new):
        return new

    def _union_traffic(self, new):
        return new

    @property
    def vertex(self):
        return self._vertex.vertex if self._vertex.type == "" else self._vertex

    @vertex.setter
    def vertex(self, _vertex):
        if isinstance(_vertex, HsVertex):
            self._vertex.vertex = _vertex.vertex
            self._vertex.type = _vertex.type

        else:
            self._vertex.vertex = _vertex

    @property
    def hs_class(self):
        return self._hs_class

    @hs_class.setter
    def hs_class(self, value):
        self._hs_class = value

    @property
    def hstype(self):
        return self._hstype

    @hstype.setter
    def hstype(self, value):
        self._hstype = value

    @property
    def simplex(self):
        return self._simplex

    @simplex.setter
    def simplex(self, value):
        self._simplex = value

    @property
    def R(self):
        return self._R

    @R.setter
    def R(self, value):
        self._R = self.R._updateR(value)

    @property
    def partOf(self):
        return self._partOf

    @partOf.setter
    def partOf(self, value):
        self._partOf = value

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, value):
        self._t = value

    @property
    def C(self):
        return self._C

    @C.setter
    def C(self, value):
        self._C = value

    @property
    def B(self):
        return self._B

    @B.setter
    def B(self, value):
        self._B = self._B.union(value)

    @property
    def other(self):
        return self._other

    @other.setter
    def other(self, value):
        self._other = value

    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, value):
        self._N = "N" if hs_default_N and not value else value

    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        self._psi = value

    @property
    def psi_inv(self):
        return self._psi_inv

    @psi_inv.setter
    def psi_inv(self, value):
        self._psi_inv = value

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self, value):
        self._phi = value

    @property
    def phi_inv(self):
        return self._phi_inv

    @phi_inv.setter
    def phi_inv(self, value):
        self._phi_inv = value

    @property
    def traffic(self):
        return self._traffic

    @traffic.setter
    def traffic(self, value):
        self._traffic = value

    @property
    def coloured(self):
        return self._coloured

    @coloured.setter
    def coloured(self, value):
        self._coloured = value

    @property
    def special(self):
        return self._special

    @special.setter
    def special(self, value):
        self._special = value

    # # def is_sequence(self):
    # #     return
    # #     return self._special == SEQUENCE

    # def is_mandatory(self):
    #     return self._special == MANDATORY

    def is_union(self):
        return self._special == UNION

    def is_immutable(self):
        return self._special == IMMUTABLE

    def update(self, vertex="", hs_class=HS_STANDARD, hstype=NONE, simplex=None,
               R="", t=-1, C=None, B=None, other=None, N="N",
               psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):

        if vertex:
            self.vertex = vertex

        if hs_class != self._hs_class:
            self._hs_class = hs_class

        if hstype != NONE:
            self.hstype = hstype

        if simplex:
            new_simplex = []
            for v in simplex:
                new_simplex.append(v)

            self.simplex = new_simplex

        if R:
            self.R = self.R._updateR(R)

        if t >= 0:
            self.t = t

        if C:
            self.C = C

        if B:
            self.B = self.B.union(B)

        if other:
            self.other = other

        if N:
            self.N = N

        if psi != "":
            self.psi = psi

        if psi_inv != "":
            self.psi_inv = psi_inv

        if phi:
            self.phi = phi

        if phi_inv:
            self.phi_inv = phi_inv

        if partOf:
            if None in self._partOf:
                self._partOf = partOf
            else:
                self._partOf.union(partOf)

        if traffic is not None:
            self._traffic = self._traffic_upsert(self._traffic, traffic)

        if coloured is not None:
            self._coloured = self._coloured_upsert(self._coloured, coloured)

    def remove_from_boundary(self, b):
        if b in self.B:
            if self.vertex not in self._hypernetwork._boundary_exclusions:
                self._hypernetwork._boundary_exclusions.update({self.vertex: set()})

            self._hypernetwork._boundary_exclusions[self.vertex].add(b)
            self.B.remove(b)

    def _handle_Hs_union_dups(self, dup=False, hs_class=HS_STANDARD, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, N="N",
                              psi="", psi_inv="", phi="", phi_inv="", partOf=None, traffic=None, coloured=None):

        if dup:
            self._hypernetwork._add(vertex=self.vertex + "@1", hs_class=self.hs_class, hstype=self.hstype,
                                    simplex=self.simplex, R=self.R, t=self.t, C=self.C, B=self.B, N=self.N,
                                    psi=self.psi, psi_inv=self.psi_inv, phi=self.phi, phi_inv=self.phi_inv,
                                    partOf=self.partOf.union({self.vertex}),
                                    traffic=self.traffic, coloured=self.coloured)

            self._hypernetwork._add(vertex=self.vertex + "@2", hs_class=hs_class, hstype=hstype, simplex=simplex,
                                    R=R, t=t, C=C, B=B, N=N, psi=psi, psi_inv=psi_inv, phi=phi, phi_inv=phi_inv,
                                    partOf=partOf.union({self.vertex}),
                                    traffic=traffic, coloured=coloured)
            # self._hypernetwork.hypernetwork.pop(self.vertex, None)

            self.hstype = ALPHA
            self.simplex = [self.vertex + "@1", self.vertex + "@2"]
            if self.vertex in self.partOf:
                self.partOf.remove(self.vertex)

            return self.vertex + "@2"

        return self.vertex

    def _validate_alpha_R(self, simplex, R, R_comparision):
        if len(self.simplex) != len(simplex):
            return False

        if not R_comparision and self.R.reltype == R_BASIC:
            # logging.warn("%s - R=%s == %s", vertex, R, self._hypernetwork[vertex].R.name)
            return False

        if self.simplex != simplex:
            # logging.warn("%s", vertex)
            return False

        return True

    def _handle_alpha_diff_R(self, simplex=None, R=""):
        return simplex, R

    def _handle_hs_expansion(self, simplex=None, R=""):
        if (isinstance(R, str) and R == self.R.name) or (not isinstance(R, str) and R.name == self.R.name):
            # This finds the ordered list of common vertices in the simplex.
            test_simplex = [i for i, j in zip(simplex, self.simplex) if i == j]

            if self.simplex == test_simplex:
                self.simplex = simplex

            elif simplex == test_simplex:
                simplex = self.simplex

            self.R = R

        return simplex, R

    def _handle_alpha_union(self, hstype=ALPHA, simplex=None, R=""):
        if (isinstance(R, str) and R == self.R.name) or (not isinstance(R, str) and R.name == self.R.name):
            self.R = R
            for vert in simplex:
                if vert not in self.simplex:
                    self.simplex.append(vert)

            simplex = self.simplex

        return hstype, simplex, R

    def _dump(self):
        return "vertex: " + str(self.vertex) \
               + ", type: " + str(HS_TYPE[self.hstype + 1]) \
               + ", simplex: " + str(self.simplex) \
               + ", partOf: " + str(self.partOf) \
               + ", special: " + special_to_str(self.special) \
               + ((", B(" + str(self.B) + ")") if self.B != {} else "") \
               + ((", R" + ("" if self.R.name == " " else "_") + str(self.R.name)) if self.R.name else "") \
               + ((", t_" + str(self.t)) if self.t >= 0 else "") \
               + ((", C(" + str(str(c) for c in self.C) + ")") if self.C != {} else "") \
               + ((", " + str(self.N)) if self.N != "" else "") \
               + ((", f_" + str(self.psi)) if self.psi else "")

    def __str__(self):
        bres = ""

        if self.simplex:
            if self.hstype in [ALPHA, UNION_ALPHA]:
                bres = "<"
            elif self.hstype in [BETA]:
                bres = "{"
            elif self.hstype in [SEQUENCE]:
                bres = "("
            else:
                bres = ""

            new_simplex = []
            for v in self.simplex:
                # if is_sequence(v):
                #     new_simplex.append("*" + v)
                #
                # else:
                if v in self._hypernetwork.hypernetwork and self._hypernetwork.hypernetwork[v].hstype == PROPERTY:
                    new_simplex.append("~" + v)
                else:
                    new_simplex.append(v)

            bres += ", ".join(new_simplex)

            if self.hstype in [ALPHA, UNION_ALPHA, SEQUENCE]:
                bres += "; R" + (("" if self.R.name == " " else "_") + self.R.name) if self.R.name else ""
                bres += ("; psi_" + str(self.psi)) if self.psi else ""
                bres += ("; t_" + str(self.t)) if self.t >= 0 else ""
                bres += ("; C(" + ", ".join(str(c) for c in self.C) + ")") if self.C else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B != set() else ""

                if self.hstype in [SEQUENCE]:
                    bres += ")" + (("^" + self.N) if self.N else "")
                else:
                    bres += ">" + (("^" + self.N) if self.N else "")

            elif self.hstype in [BETA]:
                bres += "; R" + (("" if self.R.name == " " else "_") + self.R.name) if self.R.name else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B else ""
                bres += "}" + (("^" + self.N) if self.N else "")

            else:
                bres = ""

        child = self._hypernetwork.hypernetwork[self.vertex]
        # child = self._hypernetwork.hypernetwork[strip_special(self.vertex)]
        if child.is_immutable():
            bres = "!" + bres

        return self.vertex + "=" + bres
