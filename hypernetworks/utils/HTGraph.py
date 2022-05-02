import logging as log
import re
import textwrap
# import dot2tex

from graphviz import Graph
from hypernetworks.core.Hypersimplex import ALPHA, UNION_ALPHA, BETA, VERTEX, PROPERTY, SEQUENCE


def split_camelcase(word, max):
    split = " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', word)).split())
    return textwrap.fill(split, max)


def draw_hn(Hn, direction="", R="", vertex="", N="", A=None, show_rel=True, show_level=False,
            show_time=False, view=True, fname="/tmp/Hn", split_camel=False):
    class temp:
        clusters = {}
        dot = Graph("Hn", strict=True)

    def _add_nodes(_vertex):
        if _vertex.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
            label = ""
            first = True

            for vtx in _vertex.simplex:
                vtx_port = ""
                vtx_lbl = split_camelcase(vtx, 16) if split_camel else vtx

                if vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype not in [PROPERTY]:
                    vtx_port = vtx

                if first:
                    if vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [PROPERTY]:
                        label += "~" + vtx_lbl
                    elif vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [SEQUENCE]:
                        label += "<" + vtx_port + "> " + "(" + vtx_lbl + ")"
                    else:
                        label += "<" + vtx_port + "> " + vtx_lbl

                    first = False
                else:
                    if vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [PROPERTY]:
                        label += " | ~" + vtx_lbl
                    elif vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [SEQUENCE]:
                        label += " | <" + vtx_port + "> " + "(" + vtx_lbl + ")"
                    else:
                        label += " | <" + vtx_port + "> " + vtx_lbl

                # TODO feels a bit contrived
                if vtx_port:
                    _add_nodes(Hn.hypernetwork[vtx_port])

            if _vertex.hstype in [ALPHA, UNION_ALPHA]:
                temp.dot.attr('node', style='solid', shape='record')
            elif _vertex.hstype == BETA:
                temp.dot.attr('node', style='rounded', shape='record')
            elif _vertex.hstype == SEQUENCE:
                temp.dot.attr('node', style='dashed', shape='record')

            v = "{" + (split_camelcase(_vertex.vertex, 15) if split_camel else _vertex.vertex) \
                + (("; t_" + str(_vertex.t)) if show_time and _vertex.t > -1 else "") \
                + (("|R" + ("" if _vertex.R.name == " " else ("_" + _vertex.R.name))
                   + ("" if not _vertex.B else ("\\nB(" + ", ".join(_vertex.B) + ")")))
                   if show_rel and _vertex.R.name != "" else "") \
                + "|{" + label + "}}"

            if show_level and _vertex.N:
                temp.dot.node(name=_vertex.vertex, label=v)

                if _vertex.N in temp.clusters.keys():
                    temp.clusters[_vertex.N].append(_vertex.vertex)
                else:
                    temp.clusters.update({_vertex.N: [_vertex.vertex]})
            else:
                temp.dot.node(name=_vertex.vertex, label=v)

        elif _vertex.hstype == VERTEX:
            temp.dot.attr('node', style='solid', shape="ellipse")
            temp.dot.node(name=_vertex.vertex,
                          label=split_camelcase(_vertex.vertex, 15) if split_camel else _vertex.vertex)

            if show_level:
                if "Soup" in temp.clusters.keys():
                    temp.clusters["Soup"].append(_vertex.vertex)
                else:
                    temp.clusters.update({"Soup": [_vertex.vertex]})
    # End _add_nodes

    def _add_edges(_vertex):
        temp.dot.attr('node', style='solid', shape='record')
        for vtx in _vertex.simplex:
            vtx_hs = Hn.hypernetwork[vtx]
            vtx_port = ""

            if vtx_hs.is_immutable():
                vtx_port = vtx

            else:
                if vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype not in [PROPERTY]:
                    vtx_port = vtx

            if _vertex.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
                if vtx_port:
                    temp.dot.edge(_vertex.vertex + ":" + vtx_port, vtx_port)

            elif _vertex.hstype == VERTEX:
                temp.dot.edge(vtx_port, _vertex.vertex)

            # TODO feels a bit contrived
            if vtx_port:
                _add_edges(Hn.hypernetwork[vtx_port])
    # End _add_edges

    temp.dot.attr('node', style='solid', shape='record')
    if not Hn:
        print("WARNING: Hn empty cannot generate graph.")
        return None

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
    # texcode = dot2tex.dot2tex(temp.dot.source, format='tikz', texmode='math')
    # print(texcode)

    log.debug("... complete")

    return temp.dot.source
