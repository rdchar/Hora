import logging as log
import re
import textwrap
import networkx as nx
# import dot2tex

from graphviz import Graph
import matplotlib.pyplot as plt

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.core.Hypersimplex import ALPHA, UNION_ALPHA, BETA, VERTEX, PROPERTY, SEQUENCE


def split_camelcase(word, max):
    split = " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', word)).split())
    return textwrap.fill(split, max)


def draw_hn(hn, direction="", show_rel=True, show_levels=False, show_boundary=True, show_time=False,
            show_prop=True, show_vertex=True, view=True, fname="/tmp/Hn", split_camel=False, svg=False, png=True):

    G = Graph("Hn", strict=True)
    node_visited = []
    edge_visited = []

    def _set_shape(hs):
        if hs.hstype in [ALPHA, UNION_ALPHA]:
            G.attr('node', style='solid', shape='record')
        elif hs.hstype in [BETA]:
            G.attr('node', style='rounded', shape='record')
        elif hs.hstype in [SEQUENCE]:
            G.attr('node', style='dashed', shape='record')
    # End _set_shape

    def _add_hs(_G, hs):
        label = ""
        first = True

        for vtx in hs.simplex:
            vtx_hs = hn.hypernetwork[vtx]
            vtx_port = ""
            vtx_lbl = split_camelcase(vtx, 16) if split_camel else vtx

            if vtx in hn.hypernetwork and vtx_hs.hstype not in [PROPERTY]:
                vtx_port = vtx

            if first:
                if show_prop and vtx in hn.hypernetwork and vtx_hs.hstype in [PROPERTY]:
                    label += "~" + vtx_lbl
                elif vtx in hn.hypernetwork and vtx_hs.hstype in [SEQUENCE]:
                    label += "<" + vtx_port + "> " + "(" + vtx_lbl + ")"
                else:
                    label += "<" + vtx_port + "> " + vtx_lbl

                first = False

            else:
                if show_prop and vtx in hn.hypernetwork and vtx_hs.hstype in [PROPERTY]:
                    label += " | ~" + vtx_lbl
                elif vtx in hn.hypernetwork and vtx_hs.hstype in [SEQUENCE]:
                    label += " | <" + vtx_port + "> " + "(" + vtx_lbl + ")"
                else:
                    label += " | <" + vtx_port + "> " + vtx_lbl

            # TODO feels a bit contrived
            if vtx_port:
                if vtx_port not in node_visited:
                    node_visited.append(vtx_port)

            _set_shape(hs)

            v = "{" + (split_camelcase(hs.vertex, 15) if split_camel else hs.vertex) \
                + (("; t_" + str(hs.t)) if show_time and hs.t > -1 else "") \
                + (("|R" + ("" if hs.R.name == " " else ("_" + hs.R.name))
                   + ("" if not hs.B or not show_boundary else ("\\nB(" + ", ".join(hs.B) + ")")))
                   if show_rel and hs.R.name != "" else
                   ("" if not hs.B or not show_boundary else ("\\nB(" + ", ".join(hs.B) + ")"))) \
                + "|{" + label + "}}"

            _G.node(name=hs.vertex, label=v)
    # End _add_hs

    def _add_vertex(_G, hs):
        if show_vertex or len(hs.partOf) > 1:
            _G.node(name=hs.vertex, label=split_camelcase(hs.vertex, 15) if split_camel else hs.vertex,
                    style='solid', shape="ellipse")
    # End _add_vertex

    def _add_edges(hs):
        _set_shape(hs)

        for vtx in hs.simplex:
            vtx_hs = hn.hypernetwork[vtx]
            vtx_port = ""

            if vtx_hs.is_immutable():
                vtx_port = vtx

            else:
                if vtx in hn.hypernetwork and vtx_hs.hstype not in [PROPERTY]:
                    vtx_port = vtx

            if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
                _set_shape(hs)
                _set_shape(hn.hypernetwork[vtx_port])

                if vtx_port:
                    if vtx_hs.hstype in [VERTEX]:
                        if show_vertex or len(vtx_hs.partOf) > 1:
                            G.edge(hs.vertex + ":" + vtx_port, vtx_port)
                    else:
                        G.edge(hs.vertex + ":" + vtx_port, vtx_port)

            elif hs.hstype in [VERTEX]:
                if show_vertex or len(hs.partOf) > 1:
                    G.attr('node', style='solid', shape="ellipse")
                    G.edge(vtx_port, hs.vertex)

            # TODO feels a bit contrived
            if vtx_port:
                if vtx_port not in node_visited:
                    edge_visited.append(vtx_port)
                    _add_edges(hn.hypernetwork[vtx_port])
    # End _add_edges

    def _draw_hn():
        G.attr('node', style='solid', shape='record')

        if not hn:
            print("WARNING: Hn empty cannot generate graph.")
            return None

        log.debug("Generating Graph ...")

        for vert, hs in hn.hypernetwork.items():
            if show_levels:
                # level_name = "Soup" if hs.hstype in [VERTEX] else hs.N
                level_name = hs.N

                if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
                    with G.subgraph(name="cluster_" + level_name, edge_attr={"labelloc": "c", "len": "10"}) as SG:
                        SG.node(level_name, style="invisible", height="0", width="0", label="")
                        SG.attr(label=level_name, rank="same")
                        _add_hs(SG, hs)

                if hs.hstype in [VERTEX]:
                    with G.subgraph(name="cluster_" + level_name, edge_attr={"labelloc": "c", "len": "10"}) as SG:
                        SG.attr(label=level_name, rank="same")
                        _add_vertex(SG, hs)

            else:
                if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
                    _add_hs(G, hs)

                if hs.hstype in [VERTEX]:
                    _add_vertex(G, hs)

            _add_edges(hs)

    if show_levels:
        levels = {"Soup"}

        for name, hs in hn.hypernetwork.items():
            levels = levels.union(set(hs.N))

        for level in levels:
            subHn = Hypernetwork()

            for name, hs in hn.hypernetwork.items():
                if hs.N == level and hs.hstype not in [VERTEX]:
                    subHn.insert(hs)

                if hs.hstype in [VERTEX]:
                    subHn.insert(hs)

            _draw_hn()

    else:
        _draw_hn()

    if direction:
        G.attr(rankdir=direction)

    if png:
        G.format = 'png'
        G.render(fname, view=view)

    if svg:
        G.format = 'svg'
        G.render(fname, view=view)

    log.debug("... complete")

    return G.source


def draw_graph_from_hn(hn, fname="/tmp/Hn", direction="", engine="fdp", view=False, svg=False, png=True):
    G = Graph("test", engine=engine, strict=True)
    if direction:
        G.attr(rankdir=direction)

    for name, hs in hn.hypernetwork.items():
        for vertex in hs.simplex:
            G.edge(name, vertex)

    if png:
        G.format = 'png'
        G.render(fname, view=view)

    if svg:
        G.format = 'svg'
        G.render(fname, view=view)

    G.format = 'png'
    G.render(fname, view=view)

    return G.source
