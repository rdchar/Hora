import ray
import redis
import sys
from sems_funcs import *
from core.Hypersimplex import ALPHA, BETA, VERTEX


def psi(vertex, hn):
    print("HELLO 1")
    simplex = hn[vertex]["simplex"]
    _r = redis.Redis(host='localhost', port=6379, db=0)

    waitlist = []

    for v in simplex:
        func = hn[v]['f']
        ID = _r.get(v)

        if ID:
            ID = ray._raylet.ObjectID(ID)

        else:
            ID = run.remote(v, hn)
            # ID = getattr(sys.modules[__name__], func).remote(v)
            _r.set(v, bytes(ID))

        waitlist.append(ID)

    data = ray.get(waitlist)

    # TODO: Not sure if this is ok, as it deletes entries for each node.
    return data


@ray.remote
def run(vertex, hn):
    print("HELLO 2")
    print(hn[vertex])
    hs_type = hn[vertex]["hstype"]
    simplex = hn[vertex]["simplex"]

    if hs_type == ALPHA:
        for v in simplex:
            print(v)
            res = psi(v, hn)

    elif hs_type == BETA:
        # TODO
        res = None

    elif hs_type == VERTEX:
        func = hn[vertex]['f']
        res = getattr(sys.modules[__name__], func)(vertex, res)
    
    return res


def clear(_simplex):
    _r = redis.Redis(host='localhost', port=6379, db=0)
    for s in _simplex:
        _r.delete(s)
