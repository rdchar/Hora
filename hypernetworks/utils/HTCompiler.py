import traceback

import lark

__HN_LARK__ = "./fullHT.lark"

from hypernetworks.core.HTConfig import hs_expand_R
from hypernetworks.core.HTErrors import HnParseError
from hypernetworks.core.HTUtils import expandR


def load_parser():
    kwargs = dict(rel_to=__file__, start="start")
    parser = lark.Lark.open(__HN_LARK__, parser="lalr", **kwargs)

    return parser


def compile_hn(Hn, parser, hs_string):
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

        def rel(self, *tokens):
            return {"REL": tokens}

        def hn(self, *tokens):
            return tokens[0]

        def hs(self, *tokens):
            return [t for t in tokens]

        def assign(self, token):
            return {"VAL": str(token)}

        def alpha(self, *tokens):
            # r = None
            # where = None
            # other = []

            # for t in tokens:
            #     if isinstance(t, dict):
            #         for k, v in t.items():
            #             if k == "R":
            #                 r = v
            #             if k == "WHERE":
            #                 where = v
            #             other.append({k: v})
            #
            #         if r and not where:  # If a where hasn't been provided, then get it from relations.
            #             if r in Hn.relations:
            #                 where = [Hn.relations[r]]
            #                 if not where[0]:
            #                     where = None
            #
            #         elif r:
            #             print("WHERE", where)

            res = []
            r = ""
            for at in tokens:
                if "R" in at:
                    r = at["R"]

                if "WHERE" in at:
                    at = {"WHERE": [{"R": r}, at["WHERE"][0] if len(at["WHERE"]) == 1 else at["WHERE"]]}

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
                    if "PROPERTY" in tk:
                        res = tk
                    else:
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

        def property(self, token):
            return {"PROPERTY": str(token)}

        def r(self, *tokens):
            if len(tokens) == 0:
                return {'R': " "}  # TODO this is a cheat until I can think of a better way

            return {'R': str(tokens[0])}

        def time(self, token):
            return {'t': int(token)}

        def coordinate(self, *tokens):
            return {'COORD': [int(t) for t in tokens]}

        def boundary(self, *tokens):
            return {'B': {str(t) for t in tokens}}

        def level(self, *tokens):
            if len(tokens) == 0:
                return {'N': "N"}

            return {'N': "N" + "".join(tokens)}

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
            return {"WHERE": list(tokens)}

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

        # Rels
        # def rels(self, *tokens):
        #     print("HELLO 1", tokens)
        #     for t in tokens:
        #         if t.get("VAL"):
        #             k = t.get("VAL")
        #         else:
        #             Hn.relations[k] = t
        #
        #     return {"REL": [t for t in tokens]}

        def relation(self, *tokens):
            return {"RELATION": list(tokens)}

        def rel_assign(self, token):
            return {"R": str(token)}

        def rels_expr(self, *tokens):
            return list(tokens)

        def pred(self, token):
            return {"PRED": str(token)}

        def psis(self, *tokens):
            return [[{"VERTEX": ""}, {"VAL": str(tokens[0])}, {"psi": str(tokens[1])}]]

        # TODO
        def derived(self, *tokens):
            return {"DERIVED": [tokens]}

        def wexpr(self, *tokens):
            return {}

    try:
        tree = parser.parse(hs_string)
        # print(tree.pretty())
        transformer = HnTransformer()
        hs = transformer.transform(tree)
        Hn.parse(hs)

    except lark.exceptions.UnexpectedToken:
        print("lark exception Unexpected Token")
        traceback.print_exc()
        raise HnParseError

    except:
        traceback.print_exc()
        raise HnParseError

    finally:
        return Hn


def load_ht(fname):
    res = ""
    for line in open(fname, 'r'):
        res += line

    return res
