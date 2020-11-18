# Relation Types

LOGIC = 0
ANN = 1
LAMBDA = 2

# Node type
NONE = -1
VERTEX = 0
ALPHA = 1
BETA = 2
PROPERTY = 3

HS_TYPE = ['NONE', 'VERTEX', 'ALPHA', 'BETA', 'PROPERTY']
hstype_to_str = lambda x: HS_TYPE[x + 1]
str_to_hstype = lambda x: HS_TYPE.index(x) - 1


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
    def __init__(self, _hn, vertex, hstype=VERTEX, simplex=None, R="", t=-1,
                 B=None, N="", psi="", partOf=None, content=""):
        self._hypernetwork = _hn
        self._simplex = []

        if simplex:
            for v in simplex:
                if isinstance(v, dict):
                    if "SEQ" in v:
                        self._simplex.append("SEQ@" + v["SEQ"])
                    elif "IMM" in v:
                        self._simplex.append("IMM@" + v["IMM"])
                    elif "MAN" in v:
                        self._simplex.append("MAN@" + v["MAN"])
                    else:
                        if "PROPERTY" in v:
                            self._simplex.append(v)

                else:
                    self._simplex.append(v)

        self._partOf = set() if partOf is None else partOf
        self._vertex = HsVertex(vertex)
        self._hstype = VERTEX if hstype == NONE else hstype
        self._R = R
        self._t = t
        self._B = set() if B is None else B
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
    def B(self):
        return self._B

    @B.setter
    def B(self, value):
        self._B = value

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

    def update(self, hstype=NONE, simplex=None, R="", t=-1, B=None, N="", psi="", partOf=None):
        if hstype != NONE:
            self.hstype = hstype

        if simplex:
            new_simplex = []
            for v in simplex:
                if isinstance(v, dict):
                    key = list(v.keys())[0]
                    new_simplex.append(key + "@" + v[key])
                else:
                    new_simplex.append(v)
            # new_simplex = [("SEQ@" + v['SEQ']) if isinstance(v, dict) else v for v in simplex]
            self.simplex = new_simplex

        if R:
            self.R = R

        if t >= 0:
            self.t = t

        if B:
            self.B = B

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
               + ", type: " + str(HS_TYPE[self.hstype + 1]) \
               + ", simplex: " + str(self.simplex) \
               + ", partOf: " + str(self.partOf) \
               + ((", B(" + str(self.B) + ")") if self.B != {} else "") \
               + ((", R" + ("" if self.R == " " else "_") + str(self.R)) if self.R else "") \
               + ((", t_" + str(self.t)) if self.t >= 0 else "") \
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
                if v[:4] == "SEQ@":
                    new_simplex.append("(" + v[4:len(v)] + ")")
                elif v[:4] == "IMM@":
                    new_simplex.append("[" + v[4:len(v)] + "]")
                elif v[:4] == "MAN@":
                    new_simplex.append("!" + v[4:len(v)])
                else:
                    # print(v, self.simplex)
                    # if v in self._hypernetwork:
                    if self._hypernetwork[v].hstype == PROPERTY:
                        new_simplex.append("~" + v)
                    else:
                        new_simplex.append(v)

            bres += ", ".join(new_simplex)

            if self.hstype == ALPHA:
                bres += "; R" + (("" if self.R == " " else "_") + self.R) if self.R else ""
                bres += ("; psi_" + str(self.psi)) if self.psi else ""
                bres += ("; t_" + str(self.t)) if self.t >= 0 else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B else ""
                bres += ">"
                bres += ("^" + self.N) if self.N else ""

            elif self.hstype == BETA:
                bres += "; R" + (("" if self.R == " " else "_") + self.R) if self.R else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B else ""
                bres += "}" + (("^" + self.N) if self.N else "")

            else:
                bres = ""

        return self.vertex + "=" + bres

    def test_str(self):
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
                if v[:4] == "SEQ@":
                    new_simplex.append("(" + v[4:len(v)] + ")")
                if v[:4] == "IMM@":
                    new_simplex.append("[" + v[4:len(v)] + "]")
                if v[:4] == "MAN@":
                    new_simplex.append("!" + v[4:len(v)])
                else:
                    if self._hypernetwork[v].hstype == PROPERTY:
                        new_simplex.append("~" + v)
                    else:
                        new_simplex.append(v)

            bres += ", ".join(new_simplex)

            if self.hstype == ALPHA:
                bres += "; R" + (("" if self.R == " " else "_") + self.R) if self.R else ""
                bres += ("; psi_" + str(self.psi)) if self.psi else ""
                bres += ("; t_" + str(self.t)) if self.t >= 0 else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B else ""
                bres += ">"
                bres += ("^" + self.N) if self.N else ""

            elif self.hstype == BETA:
                bres += "; R" + (("" if self.R == " " else "_") + self.R) if self.R else ""
                bres += ("; B(" + ", ".join(self.B) + ")") if self.B else ""
                bres += "}" + (("^" + self.N) if self.N else "")

            else:
                bres = ""

        return self.vertex \
               + (" = " if self._hstype not in [VERTEX] else " is a vertex") \
               + bres
