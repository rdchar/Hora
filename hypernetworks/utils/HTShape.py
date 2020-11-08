from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.core.Hypersimplex import BETA, ALPHA
from hypernetworks.utils.HTCompiler import load_parser, compile_hn
from hypernetworks.utils.HTPaths import get_paths


def get_shape(hn, *hs):
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

    return new_hn
