import networkx as nx
import numpy as np
from graphviz import Graph


# TODO inc_parent_links may need more work
from hypernetworks.core.Hypersimplex import BETA
from hypernetworks.utils.QAnalysis import QAnalysis


def gen_simplical_complex(hn, level=None, inc_parent_links=False, parent_links_only=False, exclude_beta=False):
    if level:
        hs_at_level = hn.search(N=level)
    else:
        inc_parent_links = True
        hs_at_level = hn.soup

    parents = []
    children = set()
    sc = nx.Graph()

    for hs in hs_at_level:
        parents.append(hn.hypernetwork[hs].vertex)
        # v = v[4:len(v)] if v[:4] == "SEQ@" else v
        children.update(set(hn.hypernetwork[hs].simplex))

    edges = []

    if parent_links_only:
        for hs in parents:
            for v in hn.hypernetwork[hs].simplex:
                v = v[4:len(v)] if v[:4] == "SEQ@" else v
                if len(hn.hypernetwork[v].partOf) > 1:
                    for p in hn.hypernetwork[v].partOf:
                        if exclude_beta:
                            if hn.hypernetwork[hs].hstype != BETA and hn.hypernetwork[p].hstype != BETA:
                                edges.append((hs, p))
                        else:
                            edges.append((hs, p))
                else:
                    # TODO This seems contrived
                    if v in parents:
                        if exclude_beta:
                            if hn.hypernetwork[hs].hstype != BETA:
                                edges.append((hs, v))
                        else:
                            edges.append((hs, v))

    else:
        for hs in hs_at_level:
            if inc_parent_links:
                for v in hn.hypernetwork[hs].simplex:
                    v = v[4:len(v)] if v[:4] == "SEQ@" else v
                    if not exclude_beta:
                        edges.append((hs, v))
                    else:
                        if hn.hypernetwork[hs].hstype != BETA and hn.hypernetwork[v].hstype != BETA:
                            edges.append((hs, v))

            for n, v1 in enumerate(hn.hypernetwork[hs].simplex):
                v1 = v1[4:len(v)] if v1[:4] == "SEQ@" else v1
                for v2 in hn.hypernetwork[hs].simplex[:n]:
                    v2 = v2[4:len(v)] if v2[:4] == "SEQ@" else v2
                    edges.append((v1, v2))

    sc.add_edges_from(edges)
    sc.remove_edges_from(sc.selfloop_edges())

    return parents, list(children), sc


def simplical_complex_to_graph(sc, fname="SC", view=True):
    if isinstance(sc, list):
        g = []
        for i, n in enumerate(sc):
            if i > 0:
                g.append((n, sc[i - 1]))
        sc = nx.Graph(g)

    dot = Graph("N", strict=True, engine="neato", node_attr={'shape': 'point'})

    if not isinstance(sc, nx.classes.graph.Graph):
        sc = sc[2]

    for v in sc:
        dot.attr("node")
        dot.node(v, xlabel=v)

    for (s, e) in sc.edges:
        dot.edge(s, e)

    dot.format = "png"
    dot.render(fname, view=view)


def _get_incidence_matrix(sc, children):
    x = len(children)
    im = np.zeros([x, x], dtype=int)

    for i, v1 in enumerate(children):
        for j, v2 in enumerate(children):
            if (v1, v2) in sc.edges:
                im[i][j] = 1

    return im


def qanalysis_of_simplical_complex(sc, titles):
    im = _get_incidence_matrix(sc, titles)
    qa = QAnalysis(im, titles)
    return qa


def get_faces(sc):
    faces = []
    return faces


def get_q_near(sc, start, end):
    q_near = []
    return q_near


def get_q_connected(sc, start, end):
    q_connected = []
    return q_connected
