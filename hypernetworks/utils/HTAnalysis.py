from hypernetworks.core.Hypersimplex import PROPERTY


def ingress_egress_count(hn):
    res = {}
    for ref in hn.hypernetwork:
        hs = hn.hypernetwork[ref]

        if hs.hstype not in [PROPERTY]:
            res.update({hs.vertex: {"ingress": len(hs.simplex), "egress": len(hs.partOf)}})

    return res