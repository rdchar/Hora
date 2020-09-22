#!/usr/bin/env python

import click
import sys
import numpy as np
import logging as log
from timeit import default_timer as timer

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils.HTCompiler import load_parser, compile_hn, load_ht
from hypernetworks.utils.HTGraph import to_graph
from hypernetworks.utils.HTInOut import JSON, YAML, load_Hn, save_Hn
from hypernetworks.utils.HTSimplicalComplex import qanalysis_of_simplical_complex, gen_simplical_complex, \
    simplical_complex_to_graph

logger = log.StreamHandler(sys.stdout)
log.basicConfig(level=log.DEBUG, handlers=[logger])


def qa(sc, parents, children):
    log.debug("Parents: " + str(parents))
    log.debug("Children: " + str(children))
    Q = qanalysis_of_simplical_complex(sc, children)

    K = np.array(Q.K)
    print("K: ")
    print(K)

    Qa = Q.qcomponents
    ecc = Q.ecc
    print()
    print("Names:    " + str(np.array(children)))
    print("Q top:    " + str(Q.top_q))
    print("Q bottom: " + str(Q.bottom_q))

    print("Eccentricity:")
    for n, e in zip(children, ecc):
        print("\t" + n + " = " + format(e, "0.4f"))

    print()
    print("Q Components:")
    for i in reversed(range(len(Qa))):
        print("\t" + str(i) + ":")

        for x in Qa[i]:
            print("\t\t" + str(x))


@click.command()
@click.argument("ht")
@click.option("--name", "-n", default="Hn", help="The name to use for the Hn.")
@click.option("--nograph", is_flag=True, help="Draw graph.")
@click.option("--dir", "-d", default=".", help="Graph direction.")
@click.option("--output", "-o", default="./", help="The location of the output files.")
@click.option("--time", "-t", is_flag=True, help="Time the parsing.")
@click.option("-r", help="Relation to filter on.")
@click.option("--qanalysis", "-q", is_flag=True, help="Show QAnalysis of Hn.")
@click.option("--levelgraph", is_flag=True)
@click.option("--level", "-v")
@click.option("--incparent", is_flag=True)
@click.option("--parentonly", is_flag=True)
@click.option("--json", "-j", is_flag=True, help="Output in JSON format.")
@click.option("--yaml", "-y", is_flag=True, help="Output in YAML format.")
@click.option("--save", "-s", help="Save JSON/YAML format.")
@click.option("--string", "-g", is_flag=True, help="Output the Hn string.")
@click.option("--atomic", "-a", is_flag=True, help="Search based on mereonomic relations.")
def run(ht, name, nograph, dir, output, time, r, qanalysis, levelgraph, level,
        incparent, parentonly, json, yaml, save, string, atomic):
    start = timer()
    hn = Hypernetwork()
    parser = load_parser()

    if save:
        for file in ht.split(','):
            compile_hn(hn, parser, load_ht(file))
    else:
        if json:
            hn = load_Hn(ht, type=JSON)
        elif yaml:
            hn = load_Hn(ht, type=YAML)
        else:
            for file in ht.split(','):
                compile_hn(hn, parser, load_ht(file))

    if time:
        end = timer()
        log.debug("Parsing: " + str(end - start))

    if not nograph:
        to_graph(hn, direction=dir, fname=output + name, R=r, N=level, A=atomic, show_level=False)

    if levelgraph:
        parents, children, sc = gen_simplical_complex(hn, level=level, inc_parent_links=incparent)

        if qanalysis:
            qa(sc, parents, children)

        if levelgraph:
            simplical_complex_to_graph(sc)

    if incparent:
        sc = gen_simplical_complex(hn, level=level, inc_parent_links=incparent)
        simplical_complex_to_graph(sc)

    elif parentonly:
        sc = gen_simplical_complex(hn, level=level, parent_links_only=parentonly)
        simplical_complex_to_graph(sc)

    if save:
        if json:
            save_Hn(hn, dir + "/" + save + ".json", type=JSON)
        if yaml:
            save_Hn(hn, dir + "/" + save + ".yaml", type=YAML)

    if string:
        print(hn.test_str())


if __name__ == "__main__":
    run()
