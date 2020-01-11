import networkx as nx
import numpy as np
from graphviz import Graph


# TODO inc_parent_links may need more work
from utils.QAnalysis import QAnalysis


def gen_simplical_complex(hn, level=None, inc_parent_links=False):
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
        children.update(set(hn.hypernetwork[hs].simplex))
        # if inc_parent_links:
        #    sc.add_nodes_from(hn.hypernetwork[hs].vertex)

    for hs in hs_at_level:
        edges = []

        if inc_parent_links:
            for v in hn.hypernetwork[hs].simplex:
                edges.append((hs, v))

        for n, v1 in enumerate(hn.hypernetwork[hs].simplex):
            for v2 in hn.hypernetwork[hs].simplex[:n]:
                edges.append((v1, v2))

        sc.add_edges_from(edges)

    return parents, list(children), sc


def simplical_complex_to_graph(sc, location="/tmp", fname="SC", view=True):
    dot = Graph("N", strict=True, engine="neato", node_attr={'shape': 'point'})

    if not isinstance(sc, nx.classes.graph.Graph):
        sc = sc[2]

    for v in sc:
        dot.attr("node")
        dot.node(v, xlabel=v)

    for (s, e) in sc.edges:
        dot.edge(s, e)

    dot.format = "png"
    dot.render(location + "/" + fname, view=view)


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
