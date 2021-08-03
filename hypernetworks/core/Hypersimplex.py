# Relation Types
import copy

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
IMMUTABLE_ALPHA = 4

# Special types
NONE = -1
IMMUTABLE = 0

HS_TYPE = ['NONE', 'VERTEX', 'ALPHA', 'BETA', 'PROPERTY', 'IMMUTABLE_ALPHA']
hstype_to_str = lambda x: HS_TYPE[x + 1]
str_to_hstype = lambda x: HS_TYPE.index(x) - 1

SPECIAL_TYPE = ['NONE', 'IMMUTABLE']
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

    # @property
    # def content(self):
    #     return self._content
    #
    # @content.setter
    # def content(self, _content):
    #     self._content = _content


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
    def __init__(self, _hn, vertex, hstype=VERTEX, simplex=None, R="", t=-1, C=None,
                 B=None, N="", psi="", phi="", partOf=None, traffic=None, coloured=None):

        self._hypernetwork = _hn
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

        self._partOf = set() if partOf is None else partOf
        self._hstype = VERTEX if hstype == NONE else hstype
        self._R = HsRelation(R, reltype=R_BASIC) if isinstance(R, str) else R
        self._t = t
        self._C = [] if C is None else C
        self._B = set() if B is None else B
        self._other = []
        self._N = N
        self._psi = psi
        self._phi = phi
        self._traffic = traffic
        self._coloured = coloured

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
        # if self._R.reltype == BASIC:
        #     return self._R.name
        return self._R

    @R.setter
    def R(self, value):
        self._R = HsRelation(value, reltype=R_BASIC) if isinstance(value, str) else value
        # self._R = HsRelation(value, reltype=BASIC, content=value) if isinstance(value, str) else value

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
        self._B = value

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
        self._N = value

    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        self._psi = value

    @property
    def phi(self):
        return self._phi

    @phi.setter
    def phi(self, value):
        self._phi = value

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
    # #
    # def is_mandatory(self):
    #     return self._special == MANDATORY

    def is_immutable(self):
        return self._special == IMMUTABLE

    def update(self, hstype=NONE, simplex=None, R="", t=-1, C=None, B=None, other=None, N="",
               psi="", phi="", partOf=None, traffic=None, coloured=None):
        if hstype != NONE:
            self.hstype = hstype

        if simplex:
            new_simplex = []
            for v in simplex:
                new_simplex.append(v)

            self.simplex = new_simplex

        if R:
            self.R = R

        if t >= 0:
            self.t = t

        if C:
            self.C = C

        if B:
            self.B = B

        if other:
            self.other = other

        if N != "":
            self.N = N

        if psi != "":
            self.psi = psi

        if phi:
            self.phi = phi

        if partOf:
            if None in self._partOf:
                self._partOf = partOf
            else:
                self._partOf.union(partOf)

        if not traffic == None:
            self._traffic = traffic

        if not coloured == None:
            self._coloured = coloured

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
            if self.hstype == ALPHA:
                bres = "<"
            elif self.hstype == BETA:
                bres = "{"
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

            if self.hstype == ALPHA:
                bres += "; R" + (("" if self.R.name == " " else "_") + self.R.name) if self.R.name else ""
                bres += ("; psi_" + str(self.psi)) if self.psi else ""
                bres += ("; t_" + str(self.t)) if self.t >= 0 else ""
                bres += ("; C(" + ", ".join(str(c) for c in self.C) + ")") if self.C else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B else ""
                bres += ">" + (("^" + self.N) if self.N else "")

            elif self.hstype == BETA:
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
