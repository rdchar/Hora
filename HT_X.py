import click
import sys
import numpy as np
import logging as log
from timeit import default_timer as timer

from core.Hypernetwork import Hypernetwork
from utils.HTGraph import to_graph
from utils.HTSimplicalComplex import qanalysis_of_simplical_complex, gen_simplical_complex, simplical_complex_to_graph
from utils.HTString import load_parser, from_string, load_ht
from utils.HTInOut import save_Hn

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
@click.option("--level", "-l")
@click.option("--incparent", is_flag=True)
@click.option("--json", "-j", help="Output in JSON format.")
@click.option("--string", "-s", is_flag=True, help="Output the Hn string.")
def run(ht, name, nograph, dir, output, time, r, qanalysis, levelgraph, level, incparent, json, string):
    start = timer()
    hn = Hypernetwork()
    parser = load_parser()

    for file in ht.split(','):
        from_string(hn, parser, load_ht(file))

    if time:
        end = timer()
        log.debug("Parsing: " + str(end - start))

    if not nograph:
        to_graph(hn, direction=dir, fname=output + name, R=r, N=level, show_level=False)

    if levelgraph or qanalysis:
        parents, children, sc = gen_simplical_complex(hn, level=level, inc_parent_links=incparent)

        if qanalysis:
            qa(sc, parents, children)

        if levelgraph:
            simplical_complex_to_graph(sc)

    if json:
        save_Hn(hn, dir + "/" + json)

    if string:
        print(hn.test_str())


if __name__ == "__main__":
    run()
