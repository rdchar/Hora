#!/usr/bin/env python

from flask import Flask, request, make_response, jsonify, json, send_file
from flask_cors import CORS
import uuid

from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils.HTCompiler import compile_hn, load_parser
from hypernetworks.utils.HTGraph import to_graph
from hypernetworks.utils.HTInOut import from_data, to_data
from hypernetworks.utils.HTSpaces import get_space

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


@app.route('/hngraph', methods=['POST'])
def hn_graph():
    hn_req = []
    vertices = []

    if request.get_json():
        if 'hypernetwork' in request.get_json():
            hn_req = request.get_json()['hypernetwork']

        if 'vertices' in request.get_json():
            vertices = request.get_json()['vertices']

    # TODO add reduce BETA functionality
    # reduce_beta = request.get_json()['reduce_beta']
    # TODO add direction capability
    # direction = request.get_json()['direction']

    if hn_req and vertices:
        # TODO add reduce BETA functionality
        # reduce_beta = reduce_beta if reduce_beta else True
        hn = from_data(hn_req)
        fname = ""
        sub_hn = get_space(hn, True, True, *vertices)

        if len(sub_hn.hypernetwork) > 0:
            # TODO add direction capability
            # direction = direction if direction else "TB"
            fname = "/tmp/" + str(uuid.uuid4())
            to_graph(sub_hn, fname=fname, view=False)

        if sub_hn and fname:
            return send_file(fname + ".png", mimetype='image/png')

        else:
            response = app.response_class(
                status=400,
                mimetype="application/json"
            )

    else:
        response = make_response("Not working", 500)

    return response


@app.route('/subhn', methods=['POST'])
def subhn():
    hn_req = []
    vertices = []

    if request.get_json():
        if 'hypernetwork' in request.get_json():
            hn_req = request.get_json()['hypernetwork']

        if 'vertices' in request.get_json():
            vertices = request.get_json()['vertices']

    # TODO add reduce BETA functionality
    # reduce_beta = request.get_json()['reduce_beta']

    if hn_req and vertices:
        # TODO add reduce BETA functionality
        # reduce_beta = reduce_beta if reduce_beta else True
        hn = from_data(hn_req)
        sub_hn = get_space(hn, True, True, *vertices)

        if sub_hn:
            response = app.response_class(
                response=json.dumps(to_data(sub_hn)),
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
    app.run()
