from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.core.Hypersimplex import BETA, ALPHA, VERTEX
from hypernetworks.utils.HTCompiler import load_parser, compile_hn
from hypernetworks.utils.HTPaths import get_paths, get_underpath


def paths_to_hn(hn, *hs):
    paths = get_paths(hn, *hs)
    shape = set()
    parser = load_parser()

    for key, val in paths.items():
        path = paths.get(key)
        for p in path:
            for x in p:
                if hn.hypernetwork[x].hstype == BETA:
                    pass

                shape.add(x)

    s = ""

    # TODO not keen on using this method, i.e. convert to tet and compile to get a ne Hn.
    for f in shape:
        if hn.hypernetwork[f].hstype in [ALPHA, BETA]:
            s += str(hn.hypernetwork[f]) + "\n"

    new_hn = Hypernetwork()
    compile_hn(new_hn, parser, s)

    # TODO Remove the unnecessary vertices from each BETA
    # to_del = []
    # for name in new_hn.hypernetwork:
    #     hs = new_hn.hypernetwork[name]
    #     if hs.hstype == BETA:
    #         temp = []
    #         for v in hs.simplex:
    #             if new_hn.hypernetwork[v].hstype != VERTEX:
    #                 temp.append(v)
    #             else:
    #                 to_del.append(v)
    #
    #         if len(temp) > 0:
    #             new_hn.hypernetwork[name].simplex = ",".join(temp)
    #         else:
    #             new_hn.hypernetwork[name].simplex = []
    #             new_hn.hypernetwork[name].hstype = VERTEX

    # for d in to_del:
    #     new_hn.delete(d)

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
        if hs.hstype != VERTEX:
            hn_str += str(hs) + "\n"

    compile_hn(underpath_hn, parser, hn_str)

    return underpath_hn


