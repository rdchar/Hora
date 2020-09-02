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