from core.HTMeronymy import *

# Relation Types
from core.HTRelations import Relations

LOGIC = 0
ANN = 1

# Node type
NONE = -1
VERTEX = 0
ALPHA = 1
BETA = 2

NODE_TYPE = ['NONE', 'VERTEX', 'ALPHA', 'BETA']
node_type_to_str = lambda x: NODE_TYPE[x + 1]
str_to_node_type = lambda x: NODE_TYPE.index(x) - 1


class HsRelation:
    def __init__(self, _name, _reltype=LOGIC, _content=""):
        self._pathID = 0
        self._name = _name
        self._reltype = _reltype
        self._content = _content

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

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, _content):
        self._content = _content


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
    def __init__(self, vertex, hstype=VERTEX, simplex=None, R="", t=-1,
                 M=None, N="", psi="", partOf=None, content=""):
        self._simplex = [] if simplex is None else simplex
        self._partOf = set() if partOf is None else partOf
        self._vertex = HsVertex(vertex)
        self._hstype = VERTEX if hstype == NONE else hstype
        self._R = R
        self._t = t
        self._M = set() if M is None else M
        self._N = N
        self._psi = psi

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
        return self._R

    @R.setter
    def R(self, value):
        self._R = value

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
    def M(self):
        return self._M

    @M.setter
    def M(self, value):
        self._M = value

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

    def update(self, hstype=NONE, simplex=None, R="", t=-1, M=None, N="", psi="", partOf=None):
        if hstype != NONE:
            self.hstype = hstype

        if simplex:
            self.simplex = simplex

        if R:
            self.R = R

        if t >= 0:
            self.t = t

        if M:
            self.M = M

        if N != "":
            self.N = N

        if psi != "":
            self.psi = psi

        if partOf:
            if None in self._partOf:
                self._partOf = partOf
            else:
                self._partOf.union(partOf)

    def _dump(self):
        return "vertex: " + str(self.vertex) \
               + ", type: " + str(NODE_TYPE[self.hstype + 1]) \
               + ", simplex: " + str(self.simplex) \
               + ", partOf: " + str(self.partOf) \
               + ((", M(" + str(self.M) + ")") if self.M > M_UNKNOWN else "") \
               + ((", R" + ("" if R == " " else "_") + str(self.R)) if self.R else "") \
               + ((", t_" + str(self.t)) if self.t >= 0 else "") \
               + ((", " + str(self.N)) if self.N != "" else "") \
               + ((", f_" + str(self.psi)) if self.psi else "")

    def __str__(self):
        bres = ""
        pores = ""

        if self.simplex:
            if self.hstype == ALPHA:
                bres = "<"
            elif self.hstype == BETA:
                bres = "{"
            else:
                bres = ""

            bres += ", ".join(self.simplex)

            if self.hstype == ALPHA:
                bres += "; R" + (("" if self.R == " " else "_") + self.R) if self.R else ""
                bres += ("; t_" + str(self.t)) if self.t >= 0 else ""
                bres += ">"
                bres += ("^" + self.N) if self.N else ""
            elif self.hstype == BETA:
                bres += "}" + (("^" + self.N) if self.N else "")
            else:
                bres = ""

        if self._partOf:
            pores = " ... part of " + ", ".join(self.partOf)
        else:
            pores = ""

        return self.vertex \
               + (" = " if self._hstype != VERTEX else " is a vertex") \
               + bres \
               + pores

    def test_str(self):
        bres = ""

        if self.simplex:
            if self.hstype == ALPHA:
                bres = "<"
            elif self.hstype == BETA:
                bres = "{"
            else:
                bres = ""

            bres += ", ".join(self.simplex)

            if self.hstype == ALPHA:
                bres += "; R" + (("" if self.R == " " else "_") + self.R) if self.R else ""
                bres += ("; t_" + str(self.t)) if self.t >= 0 else ""
                bres += ">"
                bres += ("^" + self.N) if self.N else ""
            elif self.hstype == BETA:
                bres += "}" + (("^" + self.N) if self.N else "")
            else:
                bres = ""

        return self.vertex \
               + (" = " if self._hstype != VERTEX else " is a vertex") \
               + bres
