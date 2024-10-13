import lark
import traceback
from hypernetworks.core.Hypernetwork import Hypernetwork
from pprint import pprint

__HN_LARK__ = "./HoraQL.lark"


def load_parser():
    kwargs = dict(rel_to=__file__, start="start")
    parser = lark.Lark.open(__HN_LARK__, parser="lalr", **kwargs)

    return parser


# Define the transformer to parse the tree
def query_hn(Hn, parser, query):
    @lark.v_args(inline=True)
    class HTQLTransformer(lark.Transformer):
        def query(self, children):
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
        
        def value_clause(self, children):
            if children:
                if isinstance(children[0], list):
                    return {'values': children[0]}
                return {'values': children}
            return {'values': []}
        
        def rollup_value(self, children):
            return {"type": "ROLLUP", "value": children[0].value}
        
        def value_list(self, children):
            res = []

            for child in children:
                if isinstance(child, dict):
                    res.append(child)
                else:
                    res.append({"type": "VALUE", "value": child.value})

            return res
        
        def value(self, children):
            return children[0]

        def optional_boundaries(self, children):
            if children:
                return {'boundary_conditions': children[0]}  # Expecting a single expression tree
            
            return {'boundary_conditions': []}
        
        def boundary_or_expr(self, children):
            if len(children) == 1:
                return children[0]
            
            return {'type': 'OR', 'left': children[0], 'right': children[1]}
        
        def boundary_and_expr(self, children):
            if len(children) == 1:
                return children[0]
            
            return {'type': 'AND', 'left': children[0], 'right': children[1]}
        
        def boundary_not_expr(self, children):
            if len(children) == 1:
                return children[0]
            
            if children[0] == 'NOT':
                return {'type': 'NOT', 'expression': children[1]}
            
            return children[1]  # This handles the case of parentheses, like "(expression)"
        
        def boundary_expression(self, children):
            if len(children) == 1:
                return children[0]

            return children
        
        def boundary_clause(self, children):
            return children[0]

        def within_clause(self, children):
            return {"boundaries": children[0].children}
        
        def boundary_name(self, children):
            return children[0].value
        
        def expression(self, children):
            return children

        def boundaries_list(self, children):
            return [str(child) for child in children]
        
        def optional_where(self, children):
            if children:
                return {'conditions': children[0]}  # Expecting a single expression tree
            
            return {'conditions': []}
        
        def or_expr(self, children):
            if len(children) == 1:
                return children[0]

            return {'type': 'OR', 'left': children[0], 'right': children[1]}
        
        def and_expr(self, children):
            if len(children) == 1:
                return children[0]
            
            return {'type': 'AND', 'left': children[0], 'right': children[1]}
        
        def not_expr(self, children):
            if len(children) == 1:
                return children[0]
    
            if children[0] == 'NOT':
                return {'type': 'NOT', 'expression': children[1]}
    
            return children[1]  # This handles the case of parentheses, like "(expression)"
        
        def comparison(self, chilren):
            return chilren[0]

        def comparison_equal(self, children):
            return {'type': 'IN', 'value': [children[0].value]}
        
        def comparison_notequal(self, children):
            return {'type': 'NOT IN', 'value': [children[0].value]}
        
        def comparison_in(self, children):
            return {'type': 'IN', 'value': children[0]}
        
        def comparison_notin(self, children):
            return {'type': 'NOT IN', 'value': children[0]}
        
        def cname_list(self, children):
            return [str(child) for child in children]
        
        def cname(self, children):
            return children.value

        def optional_hints(self, children):
            if children:
                return {'hints': children[0]}

            return {'hints': []}
        
        def hint_list(self, children):
            return [str(child) for child in children]
        
        def hint(self, children):
            if len(children) > 0:
                return children[0]

            return children
        
        def logic_operator(self, children):
            return str(children[0])

    try:
        tree = parser.parse(query)
        # print(tree.pretty())
        transformer = HTQLTransformer()
        transformer.transform(tree)
        # Hn.parse(hs)

    except lark.exceptions.UnexpectedToken:
        print("ERROR: lark exception Unexpected Token")
        Hn.clear()
        # traceback.print_exc()
        raise 

    except:
        Hn.clear()
        # print(Hn)
        # traceback.print_exc()
        raise

    return Hn


def print_query(query):
    try:
        result = parser.parse(query)
        print(f"\nQuery: {query}\n")
        print(f"Parsed Result:")

        for v in result:
            pprint(v, width=120)

    except Exception as e:
        print(traceback.format_exc())
        print(f"Failed to parse query: {query}\nError: {e}\n")
    

queries = [
    # 'SELECT ROLLUP(field1), value2 WHERE R == fieldA AND (R IN [fieldB, fieldC] OR R NOT IN [fieldD, fieldE]) HINTS TRAVERSE_BETA, BRANCH_ONLY',
    # 'SELECT value1 WHERE R != fieldB OR (R IN [fieldX, fieldY] AND R != fieldZ) HINTS BRANCH_ONLY',
    # 'SELECT value1 WHERE (R IN [fieldA, fieldB] OR R NOT IN [fieldC]) AND R == fieldD',
    # 'SELECT ALL WHERE R == fieldA OR R NOT IN [fieldB, fieldC]',
    # 'SELECT ALL WHERE R == fieldA'
    # 'SELECT ROLLUP(field1), value2 WITHIN (boundaryA, boundaryB) WHERE R == fieldA AND (R IN [fieldB, fieldC] OR R NOT IN [fieldD, fieldE]) HINTS TRAVERSE_BETA',
    # 'SELECT value1, value2 WITHIN (boundaryX OR (boundaryY AND NOT boundaryZ)) WHERE R != fieldB OR (R IN [fieldX, fieldY] AND NOT R == fieldZ) HINTS BRANCH_ONLY',
    # 'SELECT value1 WITHIN (boundaryA AND (boundaryB OR (NOT boundaryC AND boundaryD))) WHERE (R IN [fieldA, fieldB] OR R NOT IN [fieldC]) AND R == fieldD HINTS PARTS_ONLY',
    'SELECT ALL WITHIN (boundary1 AND NOT boundary2) OR boundary3 HINTS WHOLES_ONLY',
    # 'SELECT value1 WITHIN boundaryA WHERE R == fieldX AND R NOT IN [fieldY]'
]

parser = load_parser()
Hn = Hypernetwork()

# Parse and execute example queries
for query in queries:
    query_hn(Hn, parser, query)
    print_query(query)
