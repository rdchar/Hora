#!/usr/bin/env python

import click

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils.HTCompiler import load_parser, compile_hn
from hypernetworks.utils.HTInOut import load_Hn
from hypernetworks.utils.HTMongo import load_Hn_into_mongo


@click.command()
@click.argument('name')
@click.argument('fname')
def hn_loader(name, fname):
    hn = Hypernetwork(name=name)
    parser = load_parser()

    compile_hn(hn, parser, load_Hn(fname))

    load_Hn_into_mongo(hn)
    print("Loaded ...", fname, "as", name)
