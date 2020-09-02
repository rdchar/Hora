import logging as log

from graphviz import Graph

from hypernetworks.core import ALPHA, BETA, VERTEX


def to_graph(Hn, direction="", R="", vertex="", N="", A=None, strict_meronymy=False,
             show_rel=True, show_meronymy=False, show_level=False, show_time=False,
             view=True, fname="/tmp/Hn"):

    class temp:
        clusters = {}
        dot = Graph("Hn", strict=True)

    def _add_nodes(_vertex):
        if _vertex.hstype in [ALPHA, BETA]:
            label = ""
            first = True

            for vtx in _vertex.simplex:
                if vtx[:4] == "SEQ@":
                    vtx_lbl = ("(" + vtx[4:len(vtx)] + ")")
                    vtx_port = vtx[4:len(vtx)]
                elif vtx[:4] == "IMM@":
                    vtx_lbl = ("[" + vtx[4:len(vtx)] + "]")
                    vtx_port = vtx[4:len(vtx)]
                elif vtx[:4] == "MAN@":
                    vtx_lbl = ("[" + vtx[4:len(vtx)] + "]")
                    vtx_port = vtx[4:len(vtx)]
                else:
                    vtx_lbl = vtx
                    vtx_port = vtx

                if first:
                    label += "<" + vtx_port + "> " + vtx_lbl
                    first = False
                else:
                    label += " | <" + vtx_port + "> " + vtx_lbl

                # TODO feels a bit contrived
                _add_nodes(Hn.hypernetwork[vtx_port])

            if _vertex.hstype == ALPHA:
                temp.dot.attr('node', style='solid', shape='record')
            elif _vertex.hstype == BETA:
                temp.dot.attr('node', style='rounded', shape='record')

            v = "{" + _vertex.vertex \
                + (("; R" + ("" if _vertex.R == " " else ("_" + _vertex.R)))
                   if show_rel and _vertex.R != "" else "") \
                + (("; t_" + str(_vertex.t)) if show_time and _vertex.t > -1 else "") \
                + (("; " + _vertex.N) if show_level and _vertex.N != "" else "") \
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

    def _add_edges(_vertex):
        for vtx in _vertex.simplex:
            if vtx[:4] == "SEQ@":
                vtx_port = vtx[4:len(vtx)]
            elif vtx[:4] == "IMM@":
                vtx_port = vtx[4:len(vtx)]
            elif vtx[:4] == "MAN@":
                vtx_port = vtx[4:len(vtx)]
            else:
                vtx_port = vtx

            if _vertex.hstype in [ALPHA, BETA]:
                temp.dot.edge(_vertex.vertex + ":" + vtx_port, vtx_port)
            elif _vertex.hstype == VERTEX:
                temp.dot.edge(vtx_port, _vertex.vertex)

            # TODO feels a bit contrived
            _add_edges(Hn.hypernetwork[vtx_port])

    # End _add_edges

    log.debug("Generating Graph ...")

    if any([R, N, A, vertex]):
        vertices = Hn.search(R=R, N=N, A=A, vertex=vertex)
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

    return temp.dot.source
