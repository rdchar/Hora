import json
import yaml
from core.Hypernetwork import Hypernetwork
from core.Hypersimplex import Hypersimplex, hstype_to_str, str_to_hstype

JSON = 1
YAML = 2


def to_data(Hn):
    json_out = {}

    for (k, v) in Hn.hypernetwork.items():
        temp = {}

        if v.hstype >= 0:
            temp["hstype"] = hstype_to_str(v.hstype)
        if v.simplex:
            temp["simplex"] = v.simplex
        if v.partOf:
            temp["partOf"] = list(v.partOf)
        if v.R:
            temp["R"] = v.R
        if v.t >= 0:
            temp["T"] = v.t
        if v.A:
            temp["A"] = v.A
        if v.psi:
            temp["psi"] = v.psi
        if v.N:
            temp["N"] = v.N

        json_out.update({k: temp})

    return {"name": Hn.name, "hypersimplices": json_out}


def from_data(data):
    name = ""
    # name = list(data.values())[0]
    # data = list(data.values())[1]
    if "name" in data:
        name = data["name"]

    hn = Hypernetwork(name)

    for v, d in data["hypersimplices"].items():
        vertex = v
        hstype = int(str_to_hstype(d["hstype"]))
        simplex = list(d["simplex"]) if "simplex" in d else []
        partOf = set(d["partOf"]) if "partOf" in d else set()
        R = d["R"] if "R" in d else ""
        t = int(d["t"]) if "t" in d else -1
        A = int(d["A"]) if "A" in d else set()
        psi = d["psi"] if "psi" in d else ""
        N = d["N"] if "N" in d else ""

        hn.load_hs(Hypersimplex(vertex=vertex, hstype=hstype, simplex=simplex,
                                partOf=partOf, R=R, t=t, A=A, psi=psi, N=N))

    return hn


def save_Hn(Hn, fname="", type=JSON):
    fname = (Hn.name if fname == "" else fname)

    with open(fname, 'w', encoding='utf8') as write_file:
        if type == JSON:
            json.dump(to_data(Hn), separators=(",", ": "), indent=4, fp=write_file)

        if type == YAML:
            yaml.dump(to_data(Hn), write_file, default_flow_style=False, allow_unicode=True)


def load_Hn(fname="", type=JSON):
    fname = fname

    with open(fname, "r") as read_file:
        if type == JSON:
            data = json.load(read_file)

        if type == YAML:
            data = yaml.load(read_file, Loader=yaml.FullLoader)

    return from_data(data)
