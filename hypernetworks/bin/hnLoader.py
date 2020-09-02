import click

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils import load_parser, compile_hn
from hypernetworks.utils import load_Hn
from hypernetworks.utils import save_hn


@click.command()
@click.argument('name')
@click.argument('fname')
def hn_loader(name, fname):
    hn = Hypernetwork(name=name)
    parser = load_parser()

    compile_hn(hn, parser, load_Hn(fname))

    save_hn(hn)
    print("Loaded ...", fname, "as", name)
