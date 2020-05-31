import lark
from timeit import default_timer as timer

from core.HTConfig import hs_expand_R
from core.HTUtils import expandR

__HN_LARK__ = "./fullHT.lark"


def load_parser():
    # start = timer()
    kwargs = dict(rel_to=__file__, start="start")
    parser = lark.Lark.open(__HN_LARK__, parser="lalr", **kwargs)
    # end = timer()
    # print("Loading: " + str(end - start))
    return parser


def from_string(Hn, parser, hs_string):
    @lark.v_args(inline=True)
    class HnTransformer(lark.Transformer):
        def start(self, *tokens):
            res = []
            for ht in tokens:
                if isinstance(ht, list):
                    for ht2 in ht:
                        res.append(ht2)
                else:
                    res.append(ht)
            return res

        def rels(self, *tokens):
            for t in tokens:
                if t.get("VAL"):
                    k = t.get("VAL")
                else:
                    Hn.relations[k] = t

            return {"REL": [t for t in tokens]}

        def rel(self, *tokens):
            return {"REL": tokens}

        def hn(self, *tokens):
            return tokens[0]

        def hs(self, *tokens):
            return [t for t in tokens]

        def assign(self, token):
            return {"VAL": str(token)}

        def alpha(self, *tokens):
            if hs_expand_R:
                r = None
                where = None
                simplex = None
                other = []

                for t in tokens:
                    if isinstance(t, list):
                        simplex = t

                    elif isinstance(t, dict):
                        for k, v in t.items():
                            if k == "R":
                                r = v
                            if k == "WHERE":
                                where = v
                            other.append({k: v})

                        if r and not where:  # If a where hasn't been provided, then get it from relations.
                            where = [Hn.relations[r]]
                            if not where[0]:
                                where = None

                    elif isinstance(t, str):
                        simplex = [t]

                    else:
                        print("WTF from string Alpha", tokens, "went wrong!!!")  # TODO log issue!

                if where:
                    return expandR(simplex, where, other)[0]

            res = []
            for at in tokens:
                if isinstance(at, dict):
                    if "SEQ" in at or "IMM" in at:
                        res.append({"ALPHA": [at]})
                    else:
                        res.append(at)
                else:
                    res.append({"ALPHA": at})
            return res
            # return [at if isinstance(at, dict) else {"ALPHA": at} for at in tokens]

        def beta(self, *tokens):
            return [bt if isinstance(bt, dict) else {"BETA": bt} for bt in tokens]

        def a_simplex(self, *tokens):
            return [e for e in tokens]

        def b_simplex(self, *tokens):
            return [e for e in tokens]

        def a_vertex(self, token):
            return token if isinstance(token, dict) or isinstance(token, list) else str(token)

        def vertex(self, *tokens):
            res = []
            for tk in tokens:
                if isinstance(tk, dict):
                    res.append(tk)
                elif isinstance(tk, list):
                    res.append(tk[0])  # TODO Need to test this properly
                else:
                    res = str(tk)  # TODO need to add functionality for typed
                    break

            return res

        def empty_alpha(self):
            return {"EMPTY_ALPHA": []}

        def empty_beta(self):
            return {"EMPTY_BETA": set()}

        def sequence(self, token):
            return {"SEQ": str(token)}

        def immutable(self, token):
            return {"IMM": str(token)}

        def mandatory(self, token):
            return {"MAN": str(token)}

        def r(self, *tokens):
            if len(tokens) == 0:
                return {'R': " "}  # TODO this is a cheat until I can think of a better way

            return {'R': str(tokens[0])}

        def time(self, token):
            return {'t': int(token)}

        def atomicity(self, *tokens):
            return {'A': {str(t) for t in tokens}}

        def level(self, *tokens):
            if len(tokens) == 0:
                return {'N': ""}

            return {'N': "".join(tokens)}

        def psi(self, token):
            return {'psi': str(token)}

        """
        def seq(self, *tokens):
            return [e for e in tokens]
        """

        # TODO doesn't currently do anything
        def typed(self, *tokens):
            if len(tokens) == 1:
                return {"TYPE": str(tokens[0])}

            return {"TYPE": (str(tokens[0]), str(tokens[1]))}

        def where(self, *tokens):
            return {"WHERE": [t for t in tokens]}

        def named_rel(self, *tokens):
            res = []
            rname = ""
            for t in tokens:
                # TODO need to look at this again, it's not a great way of doing this!
                if t.get("RNAME"):
                    rname = t.get("RNAME")
                elif t.get("VNAME"):
                    res.append(t.get("VNAME"))
                else:
                    res.append(t)

            if not rname:
                #  TODO log missing RNAME
                return

            return {rname: res}

        def nary(self, *tokens):
            return self.named_rel(tokens)

        def rname(self, token):
            return {"RNAME": str(token)}

        def vname(self, token):
            return {"VNAME": int(token)}

        # TODO
        def derived(self, *tokens):
            return {"DERIVED": [tokens]}

        def rel_def(self, token):
            return {}

        def lambda_expr(self, *tokens):
            return {}

    # tot_start = timer()
    # start = timer()
    tree = parser.parse(hs_string)
    # print(tree.pretty())
    # end = timer()
    # print("Parsing: " + str(end - start))

    # start = timer()
    transformer = HnTransformer()
    hs = transformer.transform(tree)
    # end = timer()
    # print("Transforming: " + str(end - start))

    # print(hs)
    # start = timer()
    Hn.parse(hs)
    # end = timer()
    # print("Hn: " + str(end - start))
    # print(Hn)
    # Hn._dump()
    # tot_end = timer()
    # print("Total: " + str(tot_end - tot_start))

    return Hn


def load_ht(fname):
    res = ""
    for line in open(fname, 'r'):
        res += line

    return res