#!/usr/bin/env python

from flask import Flask, request, make_response, jsonify, json
from flask_cors import CORS

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils.HTCompiler import compile_hn, load_parser
from hypernetworks.utils.HTGraph import to_graph
from hypernetworks.utils.HTInOut import from_data, to_data

app = Flask(__name__)
CORS(app)


@app.route('/hello_world', methods=['GET'])
def hello_world():
    response = app.response_class(
        response="Hello, World!",
        status=200,
        mimetype='text/plain'
    )
    return response


@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    hn_str = request.get_json()['str']

    if hn_str:
        hn = Hypernetwork()
        compile_hn(hn, load_parser(), hn_str)

        if hn:
            response = app.response_class(
                response=json.dumps({"dot": to_graph(hn, view=False)}),
                status=200,
                mimetype="application/json"
            )
        else:
            response = app.response_class(
                status=400,
                mimetype="application/json"
            )

    else:
        response = make_response("Not working", 500)

    return response


@app.route('/compile', methods=['POST'])
def compile():
    hn_str = request.get_json()['hn']

    if hn_str:
        hn = Hypernetwork()
        compile_hn(hn, load_parser(), hn_str)

        if hn:
            response = app.response_class(
                response=json.dumps(to_data(hn)),
                status=200,
                mimetype="application/json"
            )

        else:
            response = app.response_class(
                status=400,
                mimetype="application/json"
            )

    else:
        response = make_response("Not working", 500)

    return response


@app.route('/union', methods=['POST'])
def union():
    unions_hn_in = request.get_json()['union']
    if isinstance(unions_hn_in[0], list):
        unions_hn_in = unions_hn_in[0]

    if unions_hn_in:
        hn = Hypernetwork()

        for union_hn in unions_hn_in:
            hn = hn.union(from_data(union_hn))

        if hn:
            response = app.response_class(
                response=json.dumps(to_data(hn)),
                status=200,
                mimetype="application/json"
            )

        else:
            response = app.response_class(
                status=400,
                mimetype="application/json"
            )

    else:
        response = make_response("Not working", 500)

    return response


if __name__ == '__main__':
    app.run(debug=True)
