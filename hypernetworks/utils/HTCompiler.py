import traceback

import lark

__HN_LARK__ = "./fullHT.lark"

from hypernetworks.core.HTErrors import HnParseError
from hypernetworks.utils.HTAnalysis import check_all_vertices_count


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

        def a_assign(self, token):
            return {"VAL": str(token)}

        def alpha(self, *tokens):
            res = []
            r = ""

            for at in tokens:
                if "R" in at:
                    r = at["R"]

                if "WHERE" in at:
                    at = {"WHERE": [{"R": r}, at["WHERE"][0] if len(at["WHERE"]) == 1 else at["WHERE"]]}

                if isinstance(at, dict):
                    if "IMMUTABLE_ALPHA" in at:
                        res.append({"ALPHA": [at]})
                    else:
                        res.append(at)
                else:
                    if len(at) == 1 and isinstance(at[0], dict):
                        # TODO needs more work
                        if "SEQUENCE" in at[0]:
                            res.append({"ALPHA": [at]})
                        elif "PROPERTY" in at[0]:
                            res.append({"ALPHA": [at]})
                        else:
                            res.append({"ALPHA": [at]})
                    else:
                        res.append({"ALPHA": at})

            return res

        def beta(self, *tokens):
            return [bt if isinstance(bt, dict) else {"BETA": bt} for bt in tokens]

        def union_alpha(self, *tokens):
            new_tokens = {}
            for token in tokens[0]:
                for k, v in token.items():
                    if k == "ALPHA":
                        new_tokens.update({"UNION_ALPHA": v})
                    else:
                        new_tokens.update({k: v})

            return [new_tokens]
            # return {"UNION_ALPHA": tokens[0][0]["ALPHA"]}  # TODO Seems a bit of a hack

        def immutable_alpha(self, *tokens):
            new_tokens = {}
            for token in tokens[0]:
                for k, v in token.items():
                    if k == "ALPHA":
                        new_tokens.update({"IMMUTABLE_ALPHA": v})
                    else:
                        new_tokens.update({k: v})

            return [new_tokens]
            # return {"IMMUTABLE_ALPHA": tokens[0][0]["ALPHA"]}  # TODO Seems a bit of a hack

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

        def sequence(self, *tokens):
            return [{"SEQUENCE": [bt for bt in tokens]}]

        # def immutable(self, token):
        #     return {"IMMUTABLE_ALPHA": str(token)}

        def property(self, token):
            return {"PROPERTY": str(token)}

        def not_vertex(self, *tokens):
            # TODO add NOT to the result.  This will mean chasing through the token to capture NOT.
            return self.vertex(tokens)

        def not_alpha(self, *tokens):
            # TODO add NOT to the result.  This will mean chasing through the token to capture NOT.
            new_tokens = {}
            for token in tokens[0]:
                for k, v in token.items():
                    new_tokens.update({k: v})

            return [new_tokens]

        def not_beta(self, *tokens):
            # TODO add NOT to the result.  This will mean chasing through the token to capture NOT.
            new_tokens = {}
            for token in tokens[0]:
                for k, v in token.items():
                    new_tokens.update({k: v})

            return [new_tokens]

        def not_property(self, token):
            # TODO add NOT to the result.  This will mean chasing through the token to capture NOT.
            return self.property(token)

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

        def psi_inv(self, token):
            return {'psi_inv': str(token)}

        def phi(self, token):
            return {'phi': str(token)}

        def phi_inv(self, token):
            return {'phi_inv': str(token)}

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

        def relation(self, *tokens):
            return {"RELATION": list(tokens)}

        def rel_assign(self, token):
            return {"R": str(token)}

        def rels_expr(self, *tokens):
            return list(tokens)

        def pred(self, token):
            return {"PRED": str(token)}

        def logic_and(self, *tokens):
            return "AND"

        def logic_or(self, *tokens):
            return "OR"

        def psis(self, *tokens):
            return [[{"VERTEX": ""}, {"VAL": str(tokens[0])}, {"psi": str(tokens[1])}]]

        def phis(self, *tokens):
            return [[{"VERTEX": ""}, {"VAL": str(tokens[0])}, {"phi": str(tokens[1])}]]

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

        # Validate the Hn for consistency.
        vertex_comparison = check_all_vertices_count(Hn)
        if len(vertex_comparison) > 0:
            print("WARNING:", ", ".join(vertex_comparison), "failed the vertex check!")

    except lark.exceptions.UnexpectedToken:
        print("ERROR: lark exception Unexpected Token")
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
