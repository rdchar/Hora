import logging as log

from graphviz import Graph

from core.HTMeronymy import M_UNKNOWN, meronymy_matrix, MERONYMY
from core.Hypersimplex import ALPHA, BETA, VERTEX


def to_graph(Hn, direction="", R="", vertex="", N="", strict_meronymy=False,
             show_rel=True, show_meronymy=False, show_level=False, show_time=False,
             view=True, fname="/tmp/Hn"):

    class temp:
        clusters = {}
        dot = Graph("Hn", strict=True)

    def _add_nodes(_vertex, prev_M=M_UNKNOWN):
        if strict_meronymy and _vertex.M > M_UNKNOWN:
            if prev_M == M_UNKNOWN or meronymy_matrix[_vertex.M, prev_M]:
                prev_M = _vertex.M
            else:
                return

        if _vertex.hstype in [ALPHA, BETA]:
            label = ""
            first = True

            for vtx in _vertex.simplex:
                if first:
                    label += "<" + vtx + "> " + vtx
                    first = False
                else:
                    label += " | <" + vtx + "> " + vtx

                _add_nodes(Hn.hypernetwork[vtx], prev_M)

            if _vertex.hstype == ALPHA:
                temp.dot.attr('node', style='solid', shape='record')
            elif _vertex.hstype == BETA:
                temp.dot.attr('node', style='rounded', shape='record')

            v = "{" + _vertex.vertex\
                + (("; R" + ("" if _vertex.R == " " else ("_" + _vertex.R)))
                   if show_rel and _vertex.R != "" else "")\
                + (("; t_" + str(_vertex.t)) if show_time and _vertex.t > -1 else "")\
                + (("; M_" + MERONYMY[_vertex.M]) if show_meronymy and _vertex.M > M_UNKNOWN else "")\
                + (("; " + _vertex.N) if show_level and _vertex.N != "" else "")\
                + "|{" + label + "}}"

            if _vertex.N:
                temp.dot.node(_vertex.vertex, v)

                if _vertex.N in temp.clusters.keys():
                    temp.clusters[_vertex.N].append(_vertex.vertex)
                else:
                    temp.clusters.update({_vertex.N: [_vertex.vertex]})
            else:
                temp.dot.node(_vertex.vertex, v)

        elif _vertex.hstype == VERTEX:
            temp.dot.attr('node', shape="ellipse")
            temp.dot.node(_vertex.vertex, _vertex.vertex)

            if "Soup" in temp.clusters.keys():
                temp.clusters["Soup"].append(_vertex.vertex)
            else:
                temp.clusters.update({"Soup": [_vertex.vertex]})
    # End _add_nodes

    def _add_edges(_vertex, prev_M=M_UNKNOWN):
        if strict_meronymy and _vertex.M > M_UNKNOWN:
            if prev_M == M_UNKNOWN or meronymy_matrix[_vertex.M, prev_M]:
                prev_M = _vertex.M
            else:
                return

        for vtx in _vertex.simplex:
            if _vertex.hstype in [ALPHA, BETA]:
                temp.dot.edge(_vertex.vertex + ":" + vtx, vtx)
            elif _vertex.hstype == VERTEX:
                temp.dot.edge(vtx, _vertex.vertex)

            _add_edges(Hn._hypernetwork[vtx], prev_M)
    # End _add_edges

    log.debug("Generating Graph ...")

    if any([R, N, vertex]):
        vertices = Hn.search(R=R, N=N, vertex=vertex)
    else:
        vertices = Hn.hypernetwork.keys()

    for vert in vertices:
        _add_nodes(Hn.hypernetwork[vert])
        _add_edges(Hn.hypernetwork[vert])

    if temp.clusters:
        new_cluster = []
        for cluster in temp.clusters:
            if cluster == "N":
                new_cluster.append(0)
            elif cluster[0] == "N":
                new_cluster.append(int(cluster[1:]))
    
        last_cluster_name = ""

        for i, n in enumerate(reversed(sorted(new_cluster))):
            cluster_name = "N" + ("" if n == 0 else "{0:+}".format(n))
            cluster = temp.clusters[cluster_name]
            
            with temp.dot.subgraph(name=cluster_name) as sg:
                sg.node(cluster_name, shape="plaintext", fontsize="16")
                sg.attr(label=cluster_name, rank="same")
                for v in cluster:
                    sg.node(v)

                if last_cluster_name:
                    temp.dot.edge(last_cluster_name, cluster_name)
                last_cluster_name = cluster_name

        cluster_name = "Soup"
        with temp.dot.subgraph(name=cluster_name) as sg:
            sg.node(cluster_name, shape="plaintext", fontsize="16")
            sg.attr(label=cluster_name, rank="same", ratio="fill")
            for v in temp.clusters[cluster_name]:
                sg.node(v)
        temp.dot.edge(last_cluster_name, cluster_name)

    if direction:
        temp.dot.attr(rankdir=direction)

    temp.dot.format = 'png'
    temp.dot.render(fname, view=view)
    log.debug("... complete")

    return True
