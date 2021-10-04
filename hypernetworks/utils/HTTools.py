from copy import deepcopy

from hypernetworks.core.HTUtils import of_hstype


def passbyval(func):
    def new(*args):
        cargs = [deepcopy(arg) for arg in args]
        return func(*cargs)

    return new


def are_similar(a, b):
    c = []

    for v in b:
        c.append(v if v[:4] not in ["IMM@"] else v[4:])
        # c.append(v if v[:4] not in ["SEQ@", "IMM@"] else v[4:])

    return len(set(c).difference(set(a))) == 0 and len(set(a).difference(set(c))) == 0


# def is_seq(x):
#     return x[:4] == "SEQ@"


def is_immutable(x):
    return x[:4] == "IMM@"


def is_mandatory(x):
    return x[:4] == "MAN@"


def remove_outliers(hn, N="N", smallest_nary=2):
    for vertex in hn.hypernetwork:
        hs = hn.hypernetwork[vertex]

        if hs.N == N:
            if len(hs.simplex) > smallest_nary:
                for s in hs.simplex:
                    if len(hn.hypernetwork[s].partOf) == 1:
                        hn.delete(vertex=s)


def find_in(val, simplex):
    found = False
    for v in simplex:
        if val == remove_special(v):
            found = True
            break

    return found


def remove_all_specials(simplex):
    return [remove_special(vertex) for vertex in simplex]


def condense_all_specials(simplex):
    res = []
    for vertex in simplex:
        if isinstance(vertex, dict):
            key = list(vertex.keys())[0]
            res.append(key + "@" + vertex[key])

        else:
            res.append(vertex)

    return res


def remove_special(vert):
    return vert[4:] if is_special(vert) else vert


def is_special(vert):
    return vert[:4] in ["IMM@", "MAN@"]
    # return vert[:4] in ["SEQ@", "IMM@", "MAN@"]


def get_vertex_types(hn, *vertices):
    vertex_types = {}

    if len(vertices) == 0:
        return None

    for vertex in vertices:
        vertex_types.update({vertex: of_hstype(hn, vertex)})

    return vertex_types


def get_type_vertices(hn, *vertices):
    type_vertex = {}

    if len(vertices) == 0:
        return None

    for vertex in vertices:
        hstype = of_hstype(hn, vertex)

        if hstype in type_vertex:
            type_vertex[hstype].add(vertex)
        else:
            type_vertex.update({hstype: set([vertex])})

    return type_vertex


def get_sb_vertices(hn, *vertices):
    sb_vertices = {}

    if len(vertices) == 0:
        return None

    for vertex in vertices:
        sb = hn.hypernetwork[vertex].B

        for s in sb:
            if s in sb_vertices:
                sb_vertices[s].add(vertex)
            else:
                sb_vertices.update({s: set([vertex])})

    return sb_vertices


def get_subHn_by_semantic_boundary(hn, semantic_boundary, subHn):
    def _insert(_name, _hs):
        subHn.insert(vertex=_name, hstype=_hs.hstype, simplex=_hs.simplex,
                     R=_hs.R, t=_hs.t, C=_hs.C, B=_hs.B, N=_hs.N,
                     psi=_hs.psi, phi=_hs.phi, traffic=_hs.traffic, coloured=_hs.coloured)

        temp_phis.add(_hs.phi)
        temp_psis.add(_hs.psi)

    temp_phis = set()
    temp_psis = set()

    for name in hn.hypernetwork:
        hs = hn.hypernetwork[name]
        if semantic_boundary in hs.B:
            _insert(name, hs)

            for vertex in hs.simplex:
                v_hs = hn.hypernetwork[vertex]
                _insert(vertex, v_hs)

    for phi in temp_phis:
        if phi:
            subHn.phis[phi] = hn.phis[phi]

    for psi in temp_psis:
        if psi:
            subHn.phis[psi] = hn.phis[psi]

    return subHn
