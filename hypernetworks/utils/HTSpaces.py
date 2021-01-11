from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.core.Hypersimplex import BETA, ALPHA, VERTEX, PROPERTY
from hypernetworks.utils.HTCompiler import load_parser, compile_hn
from hypernetworks.utils.HTPaths import get_paths, get_underpath


def get_space(hn, ignore_sb, shrink_beta, *vertex_list):
    if len(vertex_list) <= 1:
        print("WARNING: get_space requires at least two vertices.")
        return None

    paths = get_paths(hn, ignore_sb, *vertex_list)
    shape = set()
    parser = load_parser()

    for key, val in paths.items():
        path = paths.get(key)

        if path is not None:
            for p in path:
                for x in p.paths:
                    for y in x:
                        shape.add(y)

    s = ""

    # TODO not keen on using this method, i.e. convert to tet and compile to get a ne Hn.
    for f in shape:
        if hn.hypernetwork[f].hstype in [ALPHA, BETA]:
            s += str(hn.hypernetwork[f]) + "\n"

    new_hn = Hypernetwork()

    if not s:
        return new_hn

    compile_hn(new_hn, parser, s)

    # TODO Remove the unnecessary vertices from each BETA
    if shrink_beta:
        to_del = []
        for name in new_hn.hypernetwork:
            hs = new_hn.hypernetwork[name]
            if hs.hstype == BETA:
                temp = []
                for v in hs.simplex:
                    if new_hn.hypernetwork[v].hstype in [VERTEX, PROPERTY] and v not in vertex_list:
                        to_del.append(v)
                    else:
                        if v in to_del:
                            del to_del[to_del.index(v)]

                        temp.append(v)

                if len(temp) > 0:
                    new_hn.hypernetwork[name].simplex = temp.copy()
                else:
                    new_hn.hypernetwork[name].simplex = []
                    new_hn.hypernetwork[name].hstype = VERTEX

        for d in to_del:
            if d in new_hn.hypernetwork:
                del new_hn.hypernetwork[d]

    return new_hn


def underpath_to_hn(hn, vertex):
    underpath_hn = Hypernetwork()
    underpath = get_underpath(hn, vertex)
    parser = load_parser()

    vertex_list = set()
    for p1 in underpath:
        for p2 in p1:
            vertex_list.add(p2)

    hn_str = ""
    for v in vertex_list:
        hs = hn.hypernetwork[v]
        if hs.hstype not in [VERTEX, PROPERTY]:
            hn_str += str(hs) + "\n"

    compile_hn(underpath_hn, parser, hn_str)

    return underpath_hn
