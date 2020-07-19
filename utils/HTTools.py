def are_similar(a, b):
    c = []

    for v in b:
        c.append(v if v[:4] not in ["SEQ@", "IMM@"] else v[4:])

    return len(set(c).difference(set(a))) == 0 and len(set(a).difference(set(c))) == 0


def is_seq(x):
    return x[:4] == "SEQ@"


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
    return vert[:4] in ["SEQ@", "IMM@", "MAN@"]