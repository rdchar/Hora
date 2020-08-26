import json

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from core.Hypernetwork import Hypernetwork
from utils.HTCompiler import load_parser, compile_hn
from utils.HTGraph import to_graph
from utils.HTInOut import to_data

app = Flask(__name__)
CORS(app)


@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    hn_str = request.get_json()

    if hn_str:
        hn = Hypernetwork()
        compile_hn(hn, load_parser(), hn_str['str'])

        response = app.response_class(
            response=to_graph(hn, view=False),
            status=200,
            mimetype='text/plain'
        )

    else:
        response = make_response("Not working", 500)

    return response


@app.route('/generate_graphql', methods=['POST'])
def generate_graphql():
    hn_str = request.get_json()

    if hn_str:
        hn = Hypernetwork()
        compile_hn(hn, load_parser(), hn_str['str'])

        response = app.response_class(
            response=to_graph(hn, view=False),
            status=200,
            mimetype='text/plain'
        )

    else:
        response = make_response("Not working", 500)

    return response


if __name__ == '__main__':
    app.run(debug=True)
