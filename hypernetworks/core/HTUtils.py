from hypernetworks.core.Hypersimplex import NONE, VERTEX, ALPHA, BETA


def expandR(simplex, where, other_decs):
    res = []
    for v in where:
        for v_i, v_v in v.items():
            _simplex = []
            r = v_i
            for v_v_v in v_v:
                if isinstance(v_v_v, dict):
                    _simplex.append(expandR(simplex, [v_v_v], other_decs))
                elif isinstance(v_v_v, int):
                    _simplex.append(simplex[v_v_v - 1])
                else:
                    print("WTF expanding R went wrong!!")  # TODO needs to be logged.

            temp = [{"ALPHA": _simplex}, {"R": r}]
            for o in other_decs:
                for k, v in o.items():
                    if k not in ["R", "WHERE"]:
                        temp.append({k: v})
            #  assumes same level.
            res.append(temp)

    return res


def of_hstype(hn, v):
    part_hstype = NONE
    v_hstype = hn.hypernetwork[v].hstype

    if v_hstype == VERTEX:
        if hn.hypernetwork[v].partOf:
            part = list(hn.hypernetwork[v].partOf)[0]
            part_hstype = hn.hypernetwork[part].hstype

    else:
        return v_hstype

    return part_hstype