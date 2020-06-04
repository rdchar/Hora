import pytest

from core.Hypernetwork import Hypernetwork
from utils.HTCompiler import load_parser, compile_hn


@pytest.fixture
def setup_hn():
    parser = load_parser()
    return parser


def test_1(setup_hn):
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        DER=<location, total-DER=<(DER-Gen); R_totalgen>>
        DER=<location, total-DER=<(DER-Gen); R_totalgen>>
    """)

    assert str(test_hn) == "total-DER=<(DER-Gen), SEQ@DER-Gen; R_totalgen>\nDER=<location, total-DER>\n"


def test_insert(setup_hn):
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        x=<a, b, c; R_x; t_1; A(y1, y2)>
    """)

    assert str(test_hn) == "x=<a, b, c; R_x; t_1; A(y1, y2)>\n"


def test_union_of_same_ALPHAs(setup_hn):
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        x=<a, b, c>
        x=<a, b, c>
    """)

    assert str(test_hn) == "x=<a, b, c>\n"


def test_union_of_same_ALPHAs_with_R(setup_hn):
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        x=<a, b, c; R_x>
        x=<a, b, c; R_x>
    """)

    assert str(test_hn) == "x=<a, b, c; R_x>\n"


def test_union_of_same_ALPHAs_with_diff_R(setup_hn):
    # TODO unsure what this should do!
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        x=<a, b, c; R_x>
        x=<a, b, c; R_y>
    """)

    assert str(test_hn) == "x=<a, b, c; R_y>\n"



def test_union_of_different_ALPHAs(setup_hn):
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        x=<a, b, c>
        x=<b, c, d>
    """)

    assert str(test_hn) == "x-1=<a, b, c>\nx={x-1, x-2}\nx-2=<b, c, d>\n"


def test_BETA_Union(setup_hn):
    test_hn = Hypernetwork()
    parser = setup_hn

    x = compile_hn(test_hn, parser, """
        x={a, b, c}
        x={b, c, d}
    """)

    assert str(test_hn) == "x={a, b, c, d}\n"