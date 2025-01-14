import lark
import traceback
from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils.HTCompiler import load_parser, compile_hn
from pprint import pprint

__HN_LARK__ = "./HoraQL.lark"


def load_query_parser():
    kwargs = dict(rel_to=__file__, start="start")
    parser = lark.Lark.open(__HN_LARK__, parser="lalr", **kwargs)

    return parser


def run_query(hn, query):
    rolledup = set()

    def _rollup(hs):
        if len(hs.partOf) == 0:
            return hs.vertex
        
        else:
            for part in hs.partOf:
                rolledup.add(_rollup(hn.hypernetwork[part]))

    def _inc_parents(_hn, hs, boundary_condition=""):
        if len(hs.partOf) > 0:
            for part in hs.partOf:
                _inc_parents(_hn, hn.hypernetwork[part])
                _hn.insert_hs(hs.vertex, hn.hypernetwork[part], 
                              boundary_percolation="BOUNDARY_PERCOLATION" in query["hints"])

    new_hn = Hypernetwork()

    pprint(query, width=200)

    q = ""

    temp_hn = Hypernetwork()

    if "ROLLUP" in query["hints"]:
        for name, hs in hn.hypernetwork.items():
            _rollup(hs)

        for roll in rolledup:
            if roll:
                temp_hn.insert_hs(roll, hn.hypernetwork[roll], 
                                  boundary_percolation="BOUNDARY_PERCOLATION" in query["hints"])
    else:
        temp_hn = hn

    if query["conditions"]:
        q = f"({query['conditions']})"
    
        if query['boundary_conditions']:
            q = f"{q} and ({query['boundary_conditions']})"

        if query['values']:
            q = f"{q} and ({query['values']})"
    
    elif query["boundary_conditions"]:
        q = f"{query['boundary_conditions']}"

        if query['values']:
            q = f"{q} and ({query['values']})"

    elif query['values']:
        q = f"{query['values']}"

    if q:
        for v, hs in temp_hn.hypernetwork.items():
            if eval(q):
                if "INC_PARENTS" in query["hints"]:
                    _inc_parents(new_hn, hs, boundary_condition=query["boundary_conditions"])

                new_hn.insert_hs(v, hs, boundary_percolation="BOUNDARY_PERCOLATION" in query["hints"])

    return new_hn


def strip_tuple(tup):
    if isinstance(tup, str):
        return tup

    return strip_tuple(tup[0])


def match(set1, set2):
    return set1 == set2


def one(set1, set2):
    return len(set1.intersection(set2)) > 0


def subset(set1, set2):
    return set1.issubset(set2) or set2.issubset(set1)


def query_hn(hn, parser, query):
    @lark.v_args(inline=True)

    class HTQLTransformer(lark.Transformer):
        def query(self, *children):
            result = {
                'values': None,
                'boundary_conditions': [],
                'conditions': [],
                'hints': []
            }

            for child in children:
                if 'values' in child:
                    result['values'] = child['values']
                if 'boundary_conditions' in child:
                    result['boundary_conditions'] = child['boundary_conditions']
                if 'conditions' in child:
                    result['conditions'] = child['conditions']
                if 'hints' in child:
                    result['hints'] = child['hints']

            return result
        
        def start(self, children):
            return children  # Return just the children of the 'start' rule
        
        def value_clause(self, *children):
            if children:
                if isinstance(children[0], list):
                    return {'values': f"{[child for child in children[0]]}"}
            
                return {'values': children[0]}

            return {'values': []}
        
        def rollup_value(self, *children):
            return {"type": "ROLLUP", "value": children[0].value}
        
        def pos_value(self, *children):
            return {"POS": f"(len(hs.simplex) >= {children[1]} and hs.simplex[{children[1]}-1] == '{children[0]}')"}
        
        def value_list(self, *children):
            child_list = []
            pos_list = []
            vertices = more_vertices = ""

            for child in children:
                if "VALUE" in child:
                    child_list.append(child["VALUE"])
                
                if "LIST" in child:
                    child_list.append(child["LIST"])

                if "POS" in child:
                    pos_list.append(child["POS"])

            if len(child_list) > 0:
                vertices = f"one(set({[child for child in child_list]}), set(hs.simplex))"

            if len(pos_list) > 0:
                more_vertices = " or ".join(pos_list)

            if vertices and more_vertices:
                vertices += " or " + more_vertices

            elif not vertices and more_vertices:
                vertices = more_vertices

            return vertices
        
        def value(self, *children):
            if "POS" in children[0]:
                return children[0]

            return {"VALUE": f"{children[0]}"}


        def optional_boundaries(self, *children):
            if children:
                return {'boundary_conditions': strip_tuple(children[0])}  # Expecting a single expression tree
            
            return {'boundary_conditions': []}
        
        def boundary_or_expr(self, *children):
            if len(children) == 1:
                return f"{children[0]}"

            left = strip_tuple(children[0])
            right = strip_tuple(children[1])

            return f"({left} or {right})"
        
        def boundary_and_expr(self, *children):
            if len(children) == 1:
                return f"{children[0]}"

            left = strip_tuple(children[0])
            right = strip_tuple(children[1])

            return f"({left} and {right})"
        
        def boundary_not_expr(self, *children):
            if len(children) == 1:
                return f"{children[0]}"
            
            return f"not {children[1]}"  # This handles the case of parentheses, like "(expression)"
        
        def boundary_match_expr(self, *children):
            return f"match(set({children[0]}), hs.B)"
        
        def boundary_subset_expr(self, *children):
            return f"subset(set({children[0]}), hs.B)"
        
        def boundary_one_expr(self, *children):
            return f"one(set({children[0]}), hs.B)"
        
        def boundary_expression(self, *children):
            if len(children) == 1:
                return f"{children[0]}"

            return f"{children}"
        
        def boundary_name(self, *children):
            return f"'{children[0]}' in hs.B"
        
        def expression(self, *children):
            return f"{children}"

        def boundary_list(self, *children):
            return f"{[child.value for child in children]}"
        
        def optional_where(self, *children):
            if children:
                return {'conditions': strip_tuple(children)}  # Expecting a single expression tree
            
            return {'conditions': []}
        
        def or_expr(self, *children):
            if len(children) == 1:
                return f"{children[0]}"

            left = strip_tuple(children[0])
            right = strip_tuple(children[1])

            return f"({left} and {right})"
        
        def and_expr(self, *children):
            if len(children) == 1:
                return f"{children[0]}"

            left = strip_tuple(children[0])
            right = strip_tuple(children[1])

            return f"({left} and {right})"
        
        def not_expr(self, *children):
            if len(children) == 1:
                return f"not ({children[0]})"
    
            return f"not ({children[1]})"  # This handles the case of parentheses, like "(expression)"
        
        def comparison(self, *children):
            return f"{children[0]}"

        def comparison_in(self, *children):
            return f"hs.R.name in {children[0]}"
        
        def comparison_notin(self, *children):
            return f"hs.R.name not in {children[0]}"
        
        def cname_list(self, *children):
            return f"{[child.value for child in children]}"
        
        def cname(self, children):
            return children.value

        def optional_hints(self, *children):
            if children:
                return {'hints': children[0]}

            return {'hints': []}
        
        def hint_list(self, *children):
            return [str(child) for child in children]
        
        def hint(self, *children):
            if len(children) > 0:
                return children[0]

            return children
        
        def logic_operator(self, *children):
            return str(children[0])

    query_res = {}
    new_hn = None

    try:
        transformer = HTQLTransformer()
        tree = parser.parse(query)
        query_res = transformer.transform(tree)
        new_hn = run_query(hn, query_res)

    except lark.exceptions.UnexpectedToken:
        print("ERROR: lark exception Unexpected Token")
        raise 

    except:
        raise

    return new_hn
    

# queries = [
#     # 'SELECT ROLLUP(field1), value2 WHERE R IN [fieldA] AND (R IN [fieldB, fieldC] OR R NOT IN [fieldD, fieldE]) HINTS TRAVERSE_BETA, BRANCH_ONLY',
#     # 'SELECT value1 WHERE R NOT IN [fieldB] OR (R IN [fieldX, fieldY] AND R NOT IN [fieldZ]) HINTS BRANCH_ONLY',
#     # 'SELECT value1 WHERE (R IN [fieldA, fieldB] OR R NOT IN [fieldC]) AND R IN [fieldD]',
#     # 'SELECT ALL WHERE R IN [application] AND R NOT IN [fieldB, fieldC]',
#     # 'SELECT ALL',
#     # 'SELECT ALL WHERE R IN [application]',
#     # 'SELECT field1, value2 WITHIN (boundaryA, boundaryB) WHERE R IN [fieldA] AND (R IN [fieldB, fieldC] OR R NOT IN [fieldD, fieldE]) HINTS TRAVERSE_BETA',
#     # 'SELECT value1, value2 WITHIN (boundaryX OR (boundaryY AND NOT boundaryZ)) WHERE R NOT IN [fieldB] OR (R IN [fieldX, fieldY] AND NOT R IN [fieldZ]) HINTS BRANCH_ONLY',
#     # 'SELECT value1 WITHIN (boundaryA AND (boundaryB OR (NOT boundaryC AND boundaryD))) WHERE (R IN [fieldA, fieldB] OR R NOT IN [fieldC]) AND R IN [fieldD] HINTS PARTS_ONLY',
#     # 'SELECT ALL WITHIN (boundary1 AND NOT boundary2) OR boundary3 HINTS WHOLES_ONLY',
#     # 'SELECT value1 WITHIN boundaryA WHERE R IN [fieldX] AND R NOT IN [fieldY]',
#     'SELECT ALL WITHIN MATCH [old, application]',
#     'SELECT ALL WITHIN ONE [old]',
#     'SELECT ALL WITHIN old',
#     'SELECT ALL WITHIN (SUBSET [boundaryA, boundaryB] AND ONE [boundaryA, boundaryB]) OR boundaryD',
# ]

# ql_parser = load_query_parser()
# hn_parser = load_parser()

# hn = Hypernetwork()

# compile_hn(hn, hn_parser, """
#     CRM=<job-booking; R; B(new, application)>
#     FM-AM=<scheduling, asset-management, job-management, field-management, field-operations; R_application; B(new, application)>
#     Billing=<billing; R_application; B(old, application)>
# """, boundary_percolation=False)

# # Parse and execute example queries
# for query in queries:
#     print(query)
#     print(query_hn(hn, ql_parser, query))
#     print()