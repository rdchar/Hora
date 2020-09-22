from rdflib import Graph, Literal
from rdflib.namespace import ClosedNamespace
from rdflib.term import URIRef

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.core.Hypersimplex import BETA, ALPHA

HS = ClosedNamespace(
    uri=URIRef(""),
    terms=[
        'part_of', 'is_a'
    ]
)


def to_RDF(hn):
    g = Graph()

    for hs in hn.hypernetwork:
        temp = hn.hypernetwork[hs]
        for part in temp.partOf:
            if hn.hypernetwork[part].hstype == BETA:
                g.add((Literal(hs), HS.is_a, Literal(part)))
            else:
                g.add((Literal(hs), HS.part_of, Literal(part)))

    return g


def from_RDF(g):
    hn = Hypernetwork()
    alpha = {}
    beta = {}

    for s, p, o in g:
        s = str(s)
        o = str(o)

        if p == HS.part_of:
            if o in alpha:
                alpha[o].append(s)
            else:
                alpha.update({o: [s]})

        elif p == HS.is_a:
            if o in beta:
                beta[o].append(s)
            else:
                beta.update({o: [s]})

    for vertex, simplex in alpha.items():
        hn.insert(vertex=vertex, hstype=ALPHA, simplex=simplex)

    for vertex, simplex in beta.items():
        hn.insert(vertex=vertex, hstype=BETA, simplex=simplex)

    return hn
