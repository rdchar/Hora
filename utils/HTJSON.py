import json
from core.Hypernetwork import Hypernetwork, M_UNKNOWN
from core.Hypersimplex import Hypersimplex


def to_json(Hn):
    json_out = {}

    for (k, v) in Hn.hypernetwork.items():
        temp = {}

        if v.hstype >= 0:
            temp["hstype"] = v.hstype
        if v.simplex:
            temp["simplex"] = v.simplex
        if v.partOf:
            temp["partOf"] = list(v.partOf)
        if v.R:
            temp["R"] = v.R
        if v.t >= 0:
            temp["T"] = v.t
        if v.M >= 0:
            temp["M"] = v.M
        if v.f:
            temp["f"] = v.f
        if v.N:
            temp["N"] = v.N

        json_out.update({k: temp})

    return {"name": Hn.name, "hypersimplices": json_out}


def from_json(data):
    name = list(data.values())[0]
    data = list(data.values())[1]
    hn = Hypernetwork(name)

    for v, d in data:
        vertex = v
        hstype = int(d["hstype"])
        simplex = list(d["simplex"]) if "simplex" in d else []
        partOf = set(d["partOf"]) if "partOf" in d else set()
        R = d["R"] if "R" in d else ""
        t = int(d["t"]) if "t" in d else -1
        M = int(d["M"]) if "M" in d else M_UNKNOWN
        f = d["f"] if "f" in d else ""
        N = d["N"] if "N" in d else ""

        hn.load_hs(Hypersimplex(vertex=vertex, hstype=hstype, simplex=simplex, partOf=partOf, R=R, t=t, M=M, f=f, N=N))

    return hn


def save_Hn(Hn, fanme=""):
    fname = (Hn.name if fanme == "" else fanme) + ".json"

    with open(fname, "w") as write_file:
        json.dump(to_json(Hn), separators=(",", ": "), indent=4, fp=write_file)


def load_Hn(fname=""):
    fname = fname + ".json"

    with open(fname, "r") as read_file:
        data = json.load(read_file)

    return from_json(data)
