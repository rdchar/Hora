import logging as log
import re
import textwrap
# import dot2tex

from graphviz import Graph

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.core.Hypersimplex import ALPHA, UNION_ALPHA, BETA, VERTEX, PROPERTY, SEQUENCE


def split_camelcase(word, max):
    split = " ".join(re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', word)).split())
    return textwrap.fill(split, max)


def draw_hn(hn, direction="", R="", vertex="", N="", A=None, show_rel=True, show_levels=False,
            show_boundary=True, show_time=False, show_prop=True, show_vertex=True,
            view=True, fname="/tmp/Hn", split_camel=False, svg=False, png=True):

    G = Graph("Hn", strict=True)
    node_visited = []
    edge_visited = []

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

            if hs.hstype in [ALPHA, UNION_ALPHA]:
                _G.attr('node', style='solid', shape='record')
            elif hs.hstype == BETA:
                _G.attr('node', style='rounded', shape='record')
            elif hs.hstype == SEQUENCE:
                _G.attr('node', style='dashed', shape='record')

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
        G.attr('node', style='solid', shape='record')

        for vtx in hs.simplex:
            vtx_hs = hn.hypernetwork[vtx]
            vtx_port = ""

            if vtx_hs.is_immutable():
                vtx_port = vtx

            else:
                if vtx in hn.hypernetwork and vtx_hs.hstype not in [PROPERTY]:
                    vtx_port = vtx

            if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
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

    def _draw_hn(subHn):
        G.attr('node', style='solid', shape='record')
        if not hn:
            print("WARNING: Hn empty cannot generate graph.")
            return None

        log.debug("Generating Graph ...")

        if any([R, N, A, vertex]):
            vertices = hn.search(R=R, N=N, A=A, vertex=vertex)
            for vert in vertices:
                _add_hs(G, hn.hypernetwork[vert])
                _add_edges(hn.hypernetwork[vert])
        else:
            for vert, hs in hn.hypernetwork.items():
                if show_levels:
                    # level_name = "Soup" if hs.hstype in [VERTEX] else hs.N
                    level_name = hs.N

                    if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
                        with G.subgraph(name="cluster_" + level_name, edge_attr={"labelloc": "c", "len": "10"}) as SG:
                            SG.attr(label=level_name)
                            _add_hs(SG, hs)

                    if hs.hstype in [VERTEX]:
                        with G.subgraph(name="cluster_" + level_name, edge_attr={"labelloc": "c", "len": "10"}) as SG:
                            SG.attr(label=level_name)
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

            _draw_hn(subHn)

    else:
        _draw_hn(hn)

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





# def draw_hn(Hn, direction="", R="", vertex="", N="", A=None, show_rel=True, show_level=False, show_boundary=True,
#             show_time=False, show_prop=True, show_vertex=True,
#             view=True, fname="/tmp/Hn", split_camel=False, lookup={}, svg=False, png=True):
#
#     clusters = {}
#     dot = Graph("Hn", strict=True)
#     node_visited = []
#     edge_visited = []
#
#     def _add_nodes(hs):
#         if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
#             label = ""
#             first = True
#
#             for vtx in hs.simplex:
#                 vtx_port = ""
#                 vtx_lbl = split_camelcase(vtx, 16) if split_camel else vtx
#                 # if lookup:
#                 #     vtx_lbl = lookup[vtx_lbl]
#
#                 if vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype not in [PROPERTY]:
#                     vtx_port = vtx
#
#                 if first:
#                     if show_prop and vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [PROPERTY]:
#                         label += "~" + vtx_lbl
#                     elif vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [SEQUENCE]:
#                         label += "<" + vtx_port + "> " + "(" + vtx_lbl + ")"
#                     else:
#                         label += "<" + vtx_port + "> " + vtx_lbl
#
#                     first = False
#
#                 else:
#                     if show_prop and vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [PROPERTY]:
#                         label += " | ~" + vtx_lbl
#                     elif vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype in [SEQUENCE]:
#                         label += " | <" + vtx_port + "> " + "(" + vtx_lbl + ")"
#                     else:
#                         label += " | <" + vtx_port + "> " + vtx_lbl
#
#                 # TODO feels a bit contrived
#                 if vtx_port:
#                     if vtx_port not in node_visited:
#                         node_visited.append(vtx_port)
#                         _add_nodes(Hn.hypernetwork[vtx_port])
#
#             if hs.hstype in [ALPHA, UNION_ALPHA]:
#                 dot.attr('node', style='solid', shape='record')
#             elif hs.hstype == BETA:
#                 dot.attr('node', style='rounded', shape='record')
#             elif hs.hstype == SEQUENCE:
#                 dot.attr('node', style='dashed', shape='record')
#
#             # if lookup:
#             #     temp_name = lookup[hs.vertex]
#             # else:
#             #     temp_name = hs.vertex
#
#             v = "{" + (split_camelcase(hs.vertex, 15) if split_camel else hs.vertex) \
#                 + (("; t_" + str(hs.t)) if show_time and hs.t > -1 else "") \
#                 + (("|R" + ("" if hs.R.name == " " else ("_" + hs.R.name))
#                    + ("" if not hs.B or not show_boundary else ("\\nB(" + ", ".join(hs.B) + ")")))
#                    if show_rel and hs.R.name != "" else
#                    ("" if not hs.B or not show_boundary else ("\\nB(" + ", ".join(hs.B) + ")"))) \
#                 + "|{" + label + "}}"
#
#             if show_level and hs.N:
#                 dot.node(name=hs.vertex, label=v)
#
#                 if hs.N in clusters.keys():
#                     clusters[hs.N].append(hs.vertex)
#                 else:
#                     clusters.update({hs.N: [hs.vertex]})
#             else:
#                 dot.node(name=hs.vertex, label=v)
#
#         elif hs.hstype in [VERTEX]:
#             if show_vertex or len(hs.partOf) > 1:
#                 dot.attr('node', style='solid', shape="ellipse")
#                 dot.node(name=hs.vertex,
#                               label=split_camelcase(hs.vertex, 15) if split_camel else hs.vertex)
#
#                 if show_level:
#                     if "Soup" in clusters.keys():
#                         clusters["Soup"].append(hs.vertex)
#                     else:
#                         clusters.update({"Soup": [hs.vertex]})
#
#     # End _add_nodes
#
#     def _add_edges(hs):
#         dot.attr('node', style='solid', shape='record')
#         for vtx in hs.simplex:
#             vtx_hs = Hn.hypernetwork[vtx]
#             vtx_port = ""
#
#             if vtx_hs.is_immutable():
#                 vtx_port = vtx
#
#             else:
#                 if vtx in Hn.hypernetwork and Hn.hypernetwork[vtx].hstype not in [PROPERTY]:
#                     vtx_port = vtx
#
#             if hs.hstype in [ALPHA, UNION_ALPHA, BETA, SEQUENCE]:
#                 if vtx_port:
#                     if vtx_hs.hstype in [VERTEX]:
#                         if show_vertex or len(vtx_hs.partOf) > 1:
#                             dot.edge(hs.vertex + ":" + vtx_port, vtx_port)
#                     else:
#                         dot.edge(hs.vertex + ":" + vtx_port, vtx_port)
#
#             elif hs.hstype in [VERTEX]:
#                 if show_vertex or len(hs.partOf) > 1:
#                     dot.edge(vtx_port, hs.vertex)
#
#             # TODO feels a bit contrived
#             if vtx_port:
#                 if vtx_port not in node_visited:
#                     edge_visited.append(vtx_port)
#                     _add_edges(Hn.hypernetwork[vtx_port])
#     # End _add_edges
#
#     def _draw_hn(subHn):
#         dot.attr('node', style='solid', shape='record')
#         if not Hn:
#             print("WARNING: Hn empty cannot generate graph.")
#             return None
#
#         log.debug("Generating Graph ...")
#
#         if any([R, N, A, vertex]):
#             vertices = Hn.search(R=R, N=N, A=A, vertex=vertex)
#         else:
#             vertices = Hn.hypernetwork.keys()
#
#         for vert in vertices:
#             _add_nodes(Hn.hypernetwork[vert])
#             _add_edges(Hn.hypernetwork[vert])
#
#         if clusters:
#             new_cluster = []
#
#             for cluster in clusters:
#                 if cluster == "N":
#                     new_cluster.append(0)
#                 elif cluster[0] == "N":
#                     new_cluster.append(int(cluster[1:]))
#
#             last_cluster_name = ""
#             new_cluster = [int(x) for x in new_cluster]
#
#             for i, n in enumerate(reversed(sorted(new_cluster))):
#                 cluster_name = (("N" if int(n) == 0 else "N+" + str(n)) if int(n) >= 0 else "N" + str(n))
#                 cluster = clusters[cluster_name]
#
#                 with dot.subgraph(name=cluster_name) as sg:
#                     sg.node(cluster_name, shape="plaintext", fontsize="16")
#                     sg.attr(label=cluster_name, rank="same")
#                     for v in cluster:
#                         sg.node(v)
#
#                     if last_cluster_name:
#                         dot.edge(last_cluster_name, cluster_name)
#                     last_cluster_name = cluster_name
#
#             cluster_name = "Soup"
#
#             with dot.subgraph(name=cluster_name) as sg:
#                 sg.node(cluster_name, shape="plaintext", fontsize="16")
#                 sg.attr(label=cluster_name, rank="same", ratio="fill")
#                 for v in clusters[cluster_name]:
#                     sg.node(v)
#
#             dot.edge(last_cluster_name, cluster_name)
#
#     if show_level:
#         levels = {"Soup"}
#
#         for name, hs in Hn.hypernetwork.items():
#             levels = levels.union(set(hs.N))
#
#         for level in levels:
#             subHn = Hypernetwork()
#
#             for name, hs in Hn.hypernetwork.items():
#                 if hs.N == level and hs.hstype not in [VERTEX]:
#                     subHn.insert(hs)
#
#                 if hs.hstype in [VERTEX]:
#                     subHn.insert(hs)
#
#             _draw_hn(subHn)
#
#     else:
#         _draw_hn(Hn)
#
#     if direction:
#         dot.attr(rankdir=direction)
#
#     if png:
#         dot.format = 'png'
#         dot.render(fname, view=view)
#
#     if svg:
#         dot.format = 'svg'
#         dot.render(fname, view=view)
#
#     log.debug("... complete")
#
#     return dot.source
