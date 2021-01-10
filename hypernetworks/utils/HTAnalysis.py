from copy import deepcopy

from hypernetworks.core.Hypersimplex import PROPERTY


def ingress_egress_count(hn):
    res = {}
    for ref in hn.hypernetwork:
        hs = hn.hypernetwork[ref]

        if hs.hstype not in [PROPERTY]:
            res.update({hs.vertex: {"ingress": len(hs.simplex), "egress": len(hs.partOf)}})

    return res


def check_vertex_count(hn, name, vertices_list):
    def _check_vertex_count(_rel, _vertices_list):
        if not _rel:
            return []

        if isinstance(_rel, list):
            for val in _rel:
                _vertices_list = _check_vertex_count(val, _vertices_list)

        elif isinstance(_rel, dict):
            if "VNAME" in _rel:
                num = int(_rel["VNAME"])
                if num in _vertices_list:
                    _vertices_list.remove(num)
                else:
                    if num not in vertices_list:
                        _vertices_list.append(num)

        else:
            print("Check vertex count problem", _rel, "found!")

        return _vertices_list
    # End _check_vertex_count

    rel = hn.relations[name]
    vl = deepcopy(vertices_list)

    return len(_check_vertex_count(rel, vl)) == 0


def check_all_vertices_count(hn):
    res = []

    for name in hn.hypernetwork:
        hs = hn.hypernetwork[name]
        vertices_list = [i for i in range(1, len(hs.simplex) + 1)]

        if hs.R in hn.relations:
            if not check_vertex_count(hn, hs.R, vertices_list):
                res.append(name)

    return res
