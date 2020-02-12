import ray
import redis
import sys
from sems_funcs import *
from core.Hypersimplex import ALPHA, BETA, VERTEX


def run(vertex, hn):
    simplex = hn[vertex]["simplex"]
    _r = redis.Redis(host='localhost', port=6379, db=0)

    waitlist = []

    for v in simplex:
        func = hn[v]['psi']
        ID = _r.get(v)

        if ID:
            ID = ray._raylet.ObjectID(ID)

        else:
            ID = getattr(sys.modules[__name__], func).remote(v)
            _r.set(v, bytes(ID))

        waitlist.append(ID)

    data = ray.get(waitlist)

    # TODO: Not sure if this is ok, as it deletes entries for each node.
    return data


def clear(_simplex):
    _r = redis.Redis(host='localhost', port=6379, db=0)
    for s in _simplex:
        _r.delete(s)


def psi(vertex, hn):
    hs_type = hn[vertex]["hstype"]

    if hs_type == ALPHA:
        res = run(vertex, hn)

    elif hs_type == BETA:
        # TODO
        res = None
        pass

    elif hs_type == VERTEX:
        # TODO
        res = None
        pass

    func = hn[vertex]['psi']
    
    ID = getattr(sys.modules[__name__], func).remote(vertex, res)
    res = ray.get(ID)
    
    return res
    